"""
Tests for Lab 19: API Requests and Caching

All API calls are mocked — no network connection needed to run tests.
"""

import time
from unittest.mock import patch, Mock

import pytest
from crypto import get_price, get_prices_batch, CoinCache, get_price_cached


# ---------------------------------------------------------------------------
# Helpers: build fake responses so tests don't hit the real API
# ---------------------------------------------------------------------------

def _mock_response(json_data, status_code=200):
    """Create a mock requests.Response with the given JSON and status."""
    mock = Mock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


# ---------------------------------------------------------------------------
# Task 1: get_price
# ---------------------------------------------------------------------------

class TestGetPrice:
    """Fetch a single coin's price from the API."""

    @patch("crypto.requests.get")
    def test_returns_price_as_float(self, mock_get):
        mock_get.return_value = _mock_response({"bitcoin": {"usd": 65432.10}})

        price = get_price("bitcoin", "fake-key")

        assert isinstance(price, float)
        assert price == 65432.10

    @patch("crypto.requests.get")
    def test_passes_correct_params(self, mock_get):
        mock_get.return_value = _mock_response({"ethereum": {"usd": 3456.78}})

        get_price("ethereum", "my-api-key")

        mock_get.assert_called_once()
        _, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        assert params["ids"] == "ethereum"
        assert params["vs_currencies"] == "usd"
        assert params["x_cg_demo_api_key"] == "my-api-key"

    @patch("crypto.requests.get")
    def test_raises_on_non_200(self, mock_get):
        mock_get.return_value = _mock_response({}, status_code=429)

        with pytest.raises(RuntimeError):
            get_price("bitcoin", "fake-key")


# ---------------------------------------------------------------------------
# Task 2: get_prices_batch
# ---------------------------------------------------------------------------

class TestGetPricesBatch:
    """Fetch multiple coins in one API call."""

    @patch("crypto.requests.get")
    def test_returns_dict_of_prices(self, mock_get):
        mock_get.return_value = _mock_response({
            "bitcoin": {"usd": 65000.0},
            "ethereum": {"usd": 3400.0},
            "solana": {"usd": 120.0},
        })

        result = get_prices_batch(["bitcoin", "ethereum", "solana"], "fake-key")

        assert result == {
            "bitcoin": 65000.0,
            "ethereum": 3400.0,
            "solana": 120.0,
        }

    @patch("crypto.requests.get")
    def test_makes_single_api_call(self, mock_get):
        mock_get.return_value = _mock_response({
            "bitcoin": {"usd": 65000.0},
            "ethereum": {"usd": 3400.0},
        })

        get_prices_batch(["bitcoin", "ethereum"], "fake-key")

        assert mock_get.call_count == 1

    @patch("crypto.requests.get")
    def test_joins_ids_with_commas(self, mock_get):
        mock_get.return_value = _mock_response({
            "bitcoin": {"usd": 65000.0},
            "solana": {"usd": 120.0},
        })

        get_prices_batch(["bitcoin", "solana"], "fake-key")

        _, kwargs = mock_get.call_args
        ids_param = kwargs.get("params", {}).get("ids", "")
        # Should contain both coins separated by comma (order may vary)
        coins = set(ids_param.split(","))
        assert coins == {"bitcoin", "solana"}

    @patch("crypto.requests.get")
    def test_raises_on_non_200(self, mock_get):
        mock_get.return_value = _mock_response({}, status_code=500)

        with pytest.raises(RuntimeError):
            get_prices_batch(["bitcoin"], "fake-key")


# ---------------------------------------------------------------------------
# Task 3: CoinCache basics
# ---------------------------------------------------------------------------

class TestCacheBasic:
    """Cache stores and retrieves prices."""

    def test_init_defaults(self):
        cache = CoinCache()
        assert cache.ttl_seconds == 60
        assert cache.hits == 0
        assert cache.misses == 0

    def test_init_custom_ttl(self):
        cache = CoinCache(ttl_seconds=30)
        assert cache.ttl_seconds == 30

    def test_put_and_get(self):
        cache = CoinCache()
        cache.put("bitcoin", 65000.0)

        price = cache.get("bitcoin")
        assert price == 65000.0

    def test_get_miss_returns_none(self):
        cache = CoinCache()
        assert cache.get("bitcoin") is None

    def test_hit_counter(self):
        cache = CoinCache()
        cache.put("bitcoin", 65000.0)

        cache.get("bitcoin")
        cache.get("bitcoin")

        assert cache.hits == 2

    def test_miss_counter(self):
        cache = CoinCache()

        cache.get("bitcoin")
        cache.get("ethereum")

        assert cache.misses == 2

    def test_put_overwrites(self):
        cache = CoinCache()
        cache.put("bitcoin", 65000.0)
        cache.put("bitcoin", 66000.0)

        assert cache.get("bitcoin") == 66000.0


# ---------------------------------------------------------------------------
# Task 4: TTL expiration
# ---------------------------------------------------------------------------

class TestCacheTTL:
    """Cache entries expire after TTL seconds."""

    def test_fresh_entry_returns_price(self):
        cache = CoinCache(ttl_seconds=60)
        cache.put("bitcoin", 65000.0)

        # Immediately after put — should be fresh
        assert cache.get("bitcoin") == 65000.0

    def test_expired_entry_returns_none(self):
        cache = CoinCache(ttl_seconds=5)
        cache.put("bitcoin", 65000.0)

        # Fake the timestamp to be 10 seconds ago
        cache._store["bitcoin"]["timestamp"] = time.time() - 10

        assert cache.get("bitcoin") is None

    def test_expired_entry_counts_as_miss(self):
        cache = CoinCache(ttl_seconds=5)
        cache.put("bitcoin", 65000.0)
        cache._store["bitcoin"]["timestamp"] = time.time() - 10

        cache.get("bitcoin")

        assert cache.misses == 1
        assert cache.hits == 0

    def test_just_within_ttl(self):
        cache = CoinCache(ttl_seconds=60)
        cache.put("bitcoin", 65000.0)

        # Set timestamp to 59 seconds ago — still within TTL
        cache._store["bitcoin"]["timestamp"] = time.time() - 59

        assert cache.get("bitcoin") == 65000.0
        assert cache.hits == 1

    def test_exactly_at_ttl_is_expired(self):
        cache = CoinCache(ttl_seconds=60)
        cache.put("bitcoin", 65000.0)

        # Set timestamp to exactly TTL seconds ago
        cache._store["bitcoin"]["timestamp"] = time.time() - 60

        assert cache.get("bitcoin") is None
        assert cache.misses == 1


# ---------------------------------------------------------------------------
# Task 5: get_price_cached (cache-aside pattern)
# ---------------------------------------------------------------------------

class TestGetPriceCached:
    """Cache-aside: check cache first, fetch on miss, store result."""

    @patch("crypto.get_price")
    def test_cache_miss_calls_api(self, mock_get_price):
        mock_get_price.return_value = 65000.0
        cache = CoinCache()

        price = get_price_cached("bitcoin", "fake-key", cache)

        assert price == 65000.0
        mock_get_price.assert_called_once_with("bitcoin", "fake-key")

    @patch("crypto.get_price")
    def test_cache_hit_skips_api(self, mock_get_price):
        cache = CoinCache()
        cache.put("bitcoin", 65000.0)

        price = get_price_cached("bitcoin", "fake-key", cache)

        assert price == 65000.0
        mock_get_price.assert_not_called()

    @patch("crypto.get_price")
    def test_stores_fetched_price_in_cache(self, mock_get_price):
        mock_get_price.return_value = 65000.0
        cache = CoinCache()

        get_price_cached("bitcoin", "fake-key", cache)

        # Second call should hit cache
        get_price_cached("bitcoin", "fake-key", cache)

        assert mock_get_price.call_count == 1  # Only one API call
        assert cache.hits == 1
        assert cache.misses == 1

    @patch("crypto.get_price")
    def test_refetches_after_expiry(self, mock_get_price):
        mock_get_price.return_value = 65000.0
        cache = CoinCache(ttl_seconds=5)

        get_price_cached("bitcoin", "fake-key", cache)

        # Expire the entry
        cache._store["bitcoin"]["timestamp"] = time.time() - 10

        mock_get_price.return_value = 66000.0
        price = get_price_cached("bitcoin", "fake-key", cache)

        assert price == 66000.0
        assert mock_get_price.call_count == 2
