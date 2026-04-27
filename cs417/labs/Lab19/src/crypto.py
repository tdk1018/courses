"""
Lab 19: API Requests and Caching

Fetch cryptocurrency prices from CoinGecko and cache them locally.
"""

import time
import requests


# CoinGecko API base URL
BASE_URL = "https://api.coingecko.com/api/v3"


def get_price(coin_id: str, api_key: str) -> float:
    """
    Fetch the current USD price of a single cryptocurrency.

    Args:
        coin_id: CoinGecko coin identifier (e.g., "bitcoin", "ethereum")
        api_key: CoinGecko Demo API key

    Returns:
        The current price in USD as a float.

    Raises:
        RuntimeError: If the API response status code is not 200.
    """
    # TODO: Task 1
    # 1. Make a GET request to BASE_URL + "/simple/price"
    #    with params: ids, vs_currencies, x_cg_demo_api_key
    # 2. Check status code — raise RuntimeError if not 200
    # 3. Parse JSON and return the USD price as a float
    pass


def get_prices_batch(coin_ids: list, api_key: str) -> dict:
    """
    Fetch USD prices for multiple coins in a single API call.

    Args:
        coin_ids: List of CoinGecko coin identifiers
        api_key: CoinGecko Demo API key

    Returns:
        Dictionary mapping coin_id to USD price.
        Example: {"bitcoin": 65432.10, "ethereum": 3456.78}

    Raises:
        RuntimeError: If the API response status code is not 200.
    """
    # TODO: Task 2
    # 1. Join coin_ids into a comma-separated string
    # 2. Make ONE GET request with the joined string as "ids"
    # 3. Check status code
    # 4. Parse JSON and flatten into {coin_id: price} dict
    pass


class CoinCache:
    """
    A time-aware cache for cryptocurrency prices.

    Stores prices with timestamps and serves them back
    until they expire (based on TTL).
    """

    def __init__(self, ttl_seconds: int = 60):
        """
        Initialize the cache.

        Args:
            ttl_seconds: How many seconds a cached entry stays fresh.
        """
        # TODO: Task 3
        # Set up: ttl_seconds, _store (empty dict), hits (0), misses (0)
        pass

    def put(self, coin_id: str, price: float):
        """
        Store a price in the cache with a timestamp.

        Args:
            coin_id: The coin identifier
            price: The USD price to cache
        """
        # TODO: Task 3
        # Store {"price": price, "timestamp": time.time()} in _store
        pass

    def get(self, coin_id: str):
        """
        Retrieve a cached price if it exists and hasn't expired.

        Args:
            coin_id: The coin identifier

        Returns:
            The cached price as a float, or None if not found / expired.
        """
        # TODO: Task 3 — basic version (just check if key exists)
        # TODO: Task 4 — add TTL check (is the entry still fresh?)
        pass


def get_price_cached(coin_id: str, api_key: str, cache: CoinCache) -> float:
    """
    Fetch a coin's price, using the cache when possible.

    Cache-aside pattern:
    1. Check the cache
    2. On hit — return cached price, skip the API
    3. On miss — fetch from API, store in cache, return price

    Args:
        coin_id: CoinGecko coin identifier
        api_key: CoinGecko Demo API key
        cache: A CoinCache instance

    Returns:
        The USD price as a float.
    """
    # TODO: Task 5
    # 1. Try cache.get(coin_id)
    # 2. If not None, return it (cache hit!)
    # 3. If None, call get_price(), store with cache.put(), return price
    pass
