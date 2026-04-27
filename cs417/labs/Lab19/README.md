# Lab 19: API Requests and Caching

## Bridge from Lab 18

In Lab 18, you read and wrote JSON files — loading structured data from disk and saving it back. But where does that JSON actually come from in the real world?

Usually: **an API**. Your program sends an HTTP request to a server, and the server sends back JSON. Every weather app, every stock ticker, every search bar that auto-completes — there's an API behind it returning JSON.

This lab takes you from reading local files to talking to a live web service. You'll fetch real cryptocurrency prices from the CoinGecko API, and then build a **cache** that saves responses so you're not hammering the server every time you need the same data.

## Background: How API Requests Work

### The Request-Response Cycle

When your program calls an API, here's what happens:

1. Your code sends an **HTTP request** to a URL (the API endpoint)
2. The server processes the request
3. The server sends back an **HTTP response** containing JSON data
4. Your code parses the JSON into Python objects

Python's `requests` library handles steps 1-3 in a single line:

```python
import requests

response = requests.get("https://api.coingecko.com/api/v3/ping")
data = response.json()  # Parse the JSON body into a Python dict
print(data)  # {'gecko_says': '(V3) To the Moon!'}
```

### API Keys

Most APIs require an **API key** — a unique string that identifies you. It lets the API provider track usage and enforce rate limits (how many requests you're allowed per minute).

For this lab, you'll use a free CoinGecko Demo key. Sign up at [coingecko.com/en/api](https://www.coingecko.com/en/api) and grab your key from the dashboard. It's free — no payment info required.

You pass the key as a query parameter:

```python
response = requests.get(
    "https://api.coingecko.com/api/v3/simple/price",
    params={
        "ids": "bitcoin",
        "vs_currencies": "usd",
        "x_cg_demo_api_key": "YOUR_KEY_HERE"
    }
)
```

### Status Codes

Every response includes a **status code** that tells you what happened:

| Code | Meaning | What to do |
|------|---------|-----------|
| 200 | OK | Parse the data |
| 429 | Too Many Requests | You hit the rate limit — slow down |
| 401 | Unauthorized | Your API key is missing or invalid |
| 500+ | Server Error | Not your fault — try again later |

Always check the status code before parsing. A 429 means you're making too many requests — which is exactly the problem caching solves.

### Why Caching Matters

Without caching, every time your program needs Bitcoin's price, it makes a network request. That's:
- **Slow** — network round trips take 100-500ms, memory lookups take microseconds
- **Wasteful** — if you checked 10 seconds ago, the price hasn't changed meaningfully
- **Risky** — hit the rate limit and you get blocked

A **cache** stores API responses locally so repeated lookups skip the network entirely. The tradeoff: cached data gets stale. A price you cached 5 minutes ago might not match the current price. How long to keep cached data — the **TTL (time to live)** — is an engineering decision with no single right answer.

## Your Task

You'll build a cryptocurrency price checker that fetches live prices and caches them intelligently. The code lives in `src/crypto.py`.

### Starter Files

```
Lab19/
├── conftest.py            # Path setup for tests
├── src/
│   └── crypto.py          # Your implementations go here
├── tests/
│   └── test_crypto.py     # Pre-written tests (mocked API)
└── notebooks/
    └── Lab19_analysis.ipynb  # Timing experiments
```

### A Note About Testing

The pre-written tests **mock** the API — they simulate responses without hitting CoinGecko's servers. This makes tests fast, deterministic, and free from rate limits. You should *also* test against the real API manually while developing (use a Python shell or a scratch script), but the graded tests don't require a network connection.

## Task 1: Fetch a Single Coin Price

Find `get_price` in `src/crypto.py`.

This function takes a `coin_id` (like `"bitcoin"`) and an `api_key`, hits the CoinGecko `/simple/price` endpoint, and returns the USD price as a float.

The endpoint URL is:
```
https://api.coingecko.com/api/v3/simple/price
```

With these query parameters:
- `ids` — the coin to look up (e.g., `"bitcoin"`)
- `vs_currencies` — always `"usd"` for this lab
- `x_cg_demo_api_key` — your API key

The response JSON looks like:
```json
{"bitcoin": {"usd": 65432.10}}
```

Your function should:
1. Make a GET request with the right parameters
2. Check that the status code is 200 — raise a `RuntimeError` with the status code if it's not
3. Parse the JSON and return just the price (the float, not the nested dict)

```bash
python -m pytest tests/ -k "TestGetPrice" -v
git add -A && git commit -m "Lab 19: Implement get_price"
```

## Task 2: Fetch Multiple Coins in One Call

Find `get_prices_batch` in `src/crypto.py`.

Making a separate API call for each coin is wasteful. CoinGecko lets you fetch multiple coins in a single request by passing a comma-separated list of IDs.

This function takes a **list** of coin IDs and an API key, makes **one** API call, and returns a dictionary mapping each coin to its USD price.

For example, `get_prices_batch(["bitcoin", "ethereum", "solana"], key)` should return:
```python
{"bitcoin": 65432.10, "ethereum": 3456.78, "solana": 123.45}
```

The trick: join the list into a comma-separated string for the `ids` parameter. The response JSON nests each coin:
```json
{"bitcoin": {"usd": 65432.10}, "ethereum": {"usd": 3456.78}, "solana": {"usd": 123.45}}
```

Your function flattens that into a simple `{coin: price}` dictionary.

```bash
python -m pytest tests/ -k "TestGetPricesBatch" -v
git add -A && git commit -m "Lab 19: Implement get_prices_batch"
```

## Task 3: Build a Cache

Find the `CoinCache` class in `src/crypto.py`.

Now you'll build the caching layer. A `CoinCache` stores prices with timestamps so you can tell how fresh they are.

Implement three things:

**`__init__(self, ttl_seconds=60)`** — Initialize the cache with:
- A `ttl_seconds` attribute (how long entries stay fresh)
- An empty dictionary called `_store` to hold cached data
- Two counters: `hits` and `misses`, both starting at 0

**`put(self, coin_id, price)`** — Store a price in the cache. Each entry in `_store` should be a dictionary with two keys: `"price"` (the float) and `"timestamp"` (the current time from `time.time()`).

**`get(self, coin_id)`** — Look up a price. For now, just return the price if the coin is in the cache, or `None` if it isn't. Update `hits` or `misses` accordingly. (You'll add TTL checking in Task 4.)

```bash
python -m pytest tests/ -k "TestCacheBasic" -v
git add -A && git commit -m "Lab 19: Implement basic CoinCache"
```

## Task 4: Add TTL Expiration

Upgrade `CoinCache.get` to check whether cached entries are still fresh.

When `get` finds an entry, compare the current time to the entry's timestamp. If the difference is greater than `ttl_seconds`, the entry is **expired** — treat it as a miss (return `None`, increment `misses`).

This is the central design decision of the lab: **what TTL would you choose for cryptocurrency prices, and why?** There's no right answer. A 10-second TTL keeps data fresh but makes more API calls. A 5-minute TTL is efficient but might show stale prices. Think about what your user actually needs.

```bash
python -m pytest tests/ -k "TestCacheTTL" -v
git add -A && git commit -m "Lab 19: Add TTL expiration"
```

## Task 5: Wire It Together

Find `get_price_cached` in `src/crypto.py`.

This function combines everything: given a `coin_id`, `api_key`, and `CoinCache` instance, it:

1. Checks the cache first
2. On a cache hit, returns the cached price (no API call)
3. On a cache miss, calls `get_price` to fetch from the API
4. Stores the fresh price in the cache
5. Returns the price

This is the **cache-aside pattern** — the most common caching strategy. The caller always goes through the cache, and the cache decides whether to serve locally or fetch fresh data.

```bash
python -m pytest tests/ -k "TestGetPriceCached" -v
git add -A && git commit -m "Lab 19: Implement get_price_cached"
```

## Analysis Notebook

Open `notebooks/Lab19_analysis.ipynb` in Google Colab (or locally if you have Jupyter).

The notebook walks you through three experiments:

1. **Uncached vs. cached** — Fetch the same coin 10 times each way. Compare total time and API call count.
2. **TTL exploration** — Try different TTL values and observe how hit rate changes.
3. **Batch efficiency** — Compare fetching 5 coins individually vs. in one batch call.

Each experiment has writeup questions. Answer them in the notebook — a few sentences each is fine.

## Key Concepts

| Concept | What It Means |
|---------|--------------|
| API (Application Programming Interface) | A server endpoint your code can call to get data |
| HTTP GET | A request that asks for data without changing anything on the server |
| API key | A credential that identifies you to the API provider |
| Status code | A number indicating whether the request succeeded (200) or failed (4xx, 5xx) |
| Rate limit | Maximum number of requests allowed per time window |
| Cache | Local storage that saves responses to avoid redundant API calls |
| TTL (Time to Live) | How long a cached entry stays valid before it's considered stale |
| Cache hit / miss | Whether the requested data was found in the cache or not |
| Cache-aside pattern | Check cache first, fetch from source on miss, store result |

## Running the Tests

```bash
cd Lab19
python -m pytest tests/ -v
```

Work through the tasks in order. Earlier tests will pass before later ones.
