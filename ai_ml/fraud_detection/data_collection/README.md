# Data collection

- `collect_kpop_trade.py` collects candidate trade posts using SerpAPI.
- It expects `SERPAPI_KEY` via `.env`.

For a team with multiple keys, consider rotating keys via an env var like:
`SERPAPI_KEYS=key1,key2,...`
