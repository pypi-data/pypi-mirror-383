from asyncio import run
from datetime import datetime
from logging import DEBUG, INFO, FileHandler, Formatter, StreamHandler, getLogger
from pathlib import Path
from pickle import dump, dumps, load, loads
from random import choice
from sys import stdout
from typing import Literal, Any, Callable, Coroutine

import aiofiles
from appdirs import user_cache_dir

from swiftshadow.cache import checkExpiry, getExpiry
from swiftshadow.exceptions import UnsupportedProxyProtocol
from swiftshadow.helpers import deduplicateProxies
from swiftshadow.models import CacheData, Provider
from swiftshadow.models import Proxy as Proxy
from swiftshadow.providers import Providers as ProvidersMap

logger = getLogger("swiftshadow")
logger.setLevel(INFO)
logFormat = Formatter("%(asctime)s - %(name)s [%(levelname)s]:%(message)s")
streamhandler = StreamHandler(stream=stdout)
streamhandler.setFormatter(logFormat)
logger.addHandler(streamhandler)


class ProxyInterface:
    """Manages proxy acquisition, caching, and rotation from various providers.

    This class handles proxy retrieval either through fresh fetching from registered providers
    or via cached data. It supports protocol filtering, country filtering, cache management,
    and automatic/manual proxy rotation.

    Attributes:
        countries (list[str]): List of ISO country codes to filter proxies by (e.g., ["US", "CA"]).
        protocol (Literal['https', 'http']): Proxy protocol to use. Defaults to 'http'.
        selectedProviders (Callable[[list[str], Literal["http", "https"]], Coroutine[Any, Any, list[Proxy]]]]): Selected list of providers to fetch proxies from. Defaults to empty meaning all available Providers.
        maxproxies (int): Maximum number of proxies to collect from providers. Defaults to 10.
        autorotate (bool): Whether to automatically rotate proxy on each get() call. Defaults to False.
        autoUpdate (bool): Whether to automatically update proxies upon class initalisation. Defaults to True.
        cachePeriod (int): Number of minutes before cache is considered expired. Defaults to 10.
        cacheFolderPath (Path): Filesystem path for cache storage. Uses system cache dir by default.
        proxies (list[Proxy]): List of available proxy objects.
        current (Proxy | None): Currently active proxy. None if no proxies available.
        cacheExpiry (datetime | None): Timestamp when cache expires. None if no cache exists.

    Example:
        ```python
        proxy_manager = ProxyInterface(
            countries=["US"],
            protocol="http",
            autoRotate=True
        )
        print(proxy_manager.get())
        ```

    Raises:
        UnsupportedProxyProtocol: If invalid protocol is specified during initialization.
        ValueError: If no proxies match filters during update().
    """

    def __init__(
        self,
        countries: list[str] = [],
        protocol: Literal["https", "http"] = "http",
        selectedProviders: list[
            Callable[
                [list[str], Literal["http", "https"]], Coroutine[Any, Any, list[Proxy]]
            ]
        ] = [],
        maxProxies: int = 10,
        autoRotate: bool = False,
        autoUpdate: bool = True,
        cachePeriod: int = 10,
        cacheFolderPath: Path | None = None,
        debug: bool = False,
        logToFile: bool = False,
    ):
        """Initializes ProxyInterface with specified configuration.

        Args:
            countries: List of ISO country codes to filter proxies. Empty list = no filtering.
            protocol: Proxy protocol to retrieve. Choose between 'http' or 'https'.
            selectedProviders (list[Providers]): Selected list of providers to fetch proxies from. Defaults to empty meaning all available Providers.
            maxProxies: Maximum proxies to collect from all providers combined.
            autoRotate: Enable automatic proxy rotation on every get() call.
            autoUpdate (bool): Whether to automatically update proxies upon class initalisation.
            cachePeriod: Cache validity duration in minutes.
            cacheFolderPath: Custom path for cache storage. Uses system cache dir if None.
            debug: Enable debug logging level when True.
            logToFile: Write logs to swiftshadow.log in cache folder when True.
        """

        self.countries: list[str] = [i.upper() for i in countries]

        if protocol not in ["https", "http"]:
            raise UnsupportedProxyProtocol(
                f"Protocol {
                    protocol
                } is not supported by swiftshadow, please choose between HTTP or HTTPS"
            )
        self.protocol: Literal["https", "http"] = protocol
        if selectedProviders != []:
            providers: list[Provider] = []
            for i in selectedProviders:
                try:
                    providers.append(ProvidersMap[i])
                except KeyError:
                    raise ValueError(
                        f"Unkown provider {i.__name__} in the list of Selected Providers."
                    )
            self.providers: list[Provider] = providers
        else:
            self.providers: list[Provider] = list(ProvidersMap.values())

        self.maxproxies: int = maxProxies
        self.autorotate: bool = autoRotate
        self.cachePeriod: int = cachePeriod
        self.configString: str = f"{maxProxies}{''.join(protocol)}{''.join(countries)}"

        if debug:
            logger.setLevel(DEBUG)

        if not cacheFolderPath:
            cacheFolderPath = Path(user_cache_dir(appname="swiftshadow"))
            cacheFolderPath.mkdir(parents=True, exist_ok=True)
            logger.debug(f"System Cache folder set at {cacheFolderPath}")
        self.cacheFolderPath: Path = cacheFolderPath

        if logToFile:
            logFileHandler = FileHandler(
                self.cacheFolderPath.joinpath("swiftshadow.log")
            )
            logFileHandler.setFormatter(logFormat)
            logger.addHandler(logFileHandler)
        self.proxies: list[Proxy] = []
        self.current: Proxy | None = None
        self.cacheExpiry: datetime | None = None
        self.autoUpdate = autoUpdate

        if self.autoUpdate:
            self.update()

    async def async_update(self):
        """
        Updates proxy list from providers or cache in async.

        First attempts to load valid proxies from cache. If cache is expired/missing,
        fetches fresh proxies from registered providers that match country and protocol filters.
        Updates cache file with new proxies if fetched from providers.

        Raises:
            ValueError: If no proxies found after provider scraping.
        """
        try:
            async with aiofiles.open(
                self.cacheFolderPath.joinpath("swiftshadow.pickle"), "rb"
            ) as cacheFile:
                pickled_bytes = await cacheFile.read()
                cache: CacheData = loads(pickled_bytes)

                if self.configString != cache.configString:
                    logger.info("Cache Invalid due to configuration changes.")
                elif not checkExpiry(cache.expiryIn):
                    self.proxies = cache.proxies
                    logger.info("Loaded proxies from cache.")
                    logger.debug(
                        f"Cache with {len(cache.proxies)} proxies, expire in {
                            cache.expiryIn
                        }"
                    )
                    self.current = self.proxies[0]
                    self.cacheExpiry = cache.expiryIn
                    logger.debug(f"Cache set to expire at {cache.expiryIn}")
                    return
                else:
                    logger.info("Cache Expired")
        except FileNotFoundError:
            logger.info("No cache found, will be created after update.")

        self.proxies = []

        for provider in self.providers:
            if self.protocol not in provider.protocols:
                continue
            if (len(self.countries) != 0) and (not provider.countryFilter):
                continue
            providerProxies: list[Proxy] = await provider.providerFunction(
                self.countries, self.protocol
            )
            logger.debug(
                f"{len(providerProxies)} proxies from {
                    provider.providerFunction.__name__
                }"
            )
            self.proxies.extend(providerProxies)

            if len(self.proxies) >= self.maxproxies:
                break

        if len(self.proxies) == 0:
            if self.protocol == "https":
                raise ValueError("No proxies were found for the current filter settings. Tip: https proxies can be rare; recommend setting protocol to http")
            raise ValueError("No proxies were found for the current filter settings.")

        self.proxies = deduplicateProxies(self.proxies)
        async with aiofiles.open(
            self.cacheFolderPath.joinpath("swiftshadow.pickle"), "wb+"
        ) as cacheFile:
            cacheExpiry = getExpiry(self.cachePeriod)
            self.cacheExpiry = cacheExpiry
            cache = CacheData(cacheExpiry, self.configString, self.proxies)
            pickled_bytes = dumps(cache)
            _ = await cacheFile.write(pickled_bytes)
        self.current = self.proxies[0]

    def update(self):
        """
        Updates proxy list from providers or cache.

        First attempts to load valid proxies from cache. If cache is expired/missing,
        fetches fresh proxies from registered providers that match country and protocol filters.
        Updates cache file with new proxies if fetched from providers.

        Raises:
            ValueError: If no proxies found after provider scraping.
        """
        try:
            with open(
                self.cacheFolderPath.joinpath("swiftshadow.pickle"), "rb"
            ) as cacheFile:
                cache: CacheData = load(cacheFile)

                if self.configString != cache.configString:
                    logger.info("Cache Invalid due to configuration changes.")
                elif not checkExpiry(cache.expiryIn):
                    self.proxies = cache.proxies
                    logger.info("Loaded proxies from cache.")
                    logger.debug(
                        f"Cache with {len(cache.proxies)} proxies, expire in {
                            cache.expiryIn
                        }"
                    )
                    self.current = self.proxies[0]
                    logger.debug(f"Cache set to expire at {cache.expiryIn}")
                    self.cacheExpiry = cache.expiryIn
                    return
                else:
                    logger.info("Cache Expired")
        except FileNotFoundError:
            logger.info("No cache found, will be created after update.")

        self.proxies = []

        for provider in self.providers:
            if self.protocol not in provider.protocols:
                continue
            if (len(self.countries) != 0) and (not provider.countryFilter):
                continue
            providerProxies: list[Proxy] = run(
                provider.providerFunction(self.countries, self.protocol)
            )
            logger.debug(
                f"{len(providerProxies)} proxies from {
                    provider.providerFunction.__name__
                }"
            )
            self.proxies.extend(providerProxies)

            if len(self.proxies) >= self.maxproxies:
                break

        if len(self.proxies) == 0:
            raise ValueError("No proxies were found for the current filter settings.")

        self.proxies = deduplicateProxies(self.proxies)
        with open(
            self.cacheFolderPath.joinpath("swiftshadow.pickle"), "wb+"
        ) as cacheFile:
            cacheExpiry = getExpiry(self.cachePeriod)
            self.cacheExpiry = cacheExpiry
            cache = CacheData(cacheExpiry, self.configString, self.proxies)
            dump(cache, cacheFile)
        self.current = self.proxies[0]

    def rotate(self, validate_cache: bool = False):
        """
        Rotates to a random proxy from available proxies.

        Args:
            validate_cache: Force cache validation before rotation when True.

        Note:
            Only required for manual rotation when autoRotate=False. Automatic rotation
            occurs during get() calls when autoRotate=True.

        Raises:
            ValueError: If validate_cache=True but no cache exists.
        """
        if validate_cache:
            if self.cacheExpiry:
                if checkExpiry(self.cacheExpiry):
                    logger.debug("Cache Expired on rotate call, updating.")
                    self.update()
            else:
                raise ValueError("No cache available but validate_cache is true.")
        self.current = choice(self.proxies)

    def get(self) -> Proxy:
        """
        Retrieves current active proxy.

        Returns:
            Proxy: Current proxy object with connection details.

        Note:
            Performs automatic rotation if autorotate=True before returning proxy.

        Raises:
            ValueError: If no proxies are available (current is None).
        """

        if self.autorotate:
            self.rotate(validate_cache=self.autoUpdate)
        if self.current:
            return self.current
        else:
            raise ValueError("No proxy available in current, current is None")
