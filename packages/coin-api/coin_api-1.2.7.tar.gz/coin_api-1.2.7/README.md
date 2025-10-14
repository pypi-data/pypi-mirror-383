# Coin API — simple CoinMarketCap scraper

A small, educational Python scraper that fetches basic data (price, 24h change, market cap) for a cryptocurrency from CoinMarketCap.

What it returns

- Price
- 24-hour change
- Market cap

Project files

- `coin_api/COIN_API.py` — contains the `Coin` class and a small demo loop when run as a module.
- `requirements.txt` — minimal dependency list (may need to add beautifulsoup4).

Requirements

- Python 3.8+
- requests
- beautifulsoup4

Install (PowerShell)

```powershell
pip install -r requirements.txt
pip install beautifulsoup4
```

Or install both directly:

```powershell
pip install requests beautifulsoup4
```

Usage (as a module)

```python
from coin_api.COIN_API import Coin

coin = Coin("bitcoin")          # coinmarketcap slug (e.g. "bitcoin", "ethereum")
data = coin.get_data()           # returns a dict or False on error
print(data)
```

Run the included demo

```powershell
python -m coin_api.COIN_API
```

Example output (subject to site HTML changes):

```json
{
  "Price": "$61,234.56",
  "24h change": "+2.34% ↗️",
  "Market cap": "$1,150,000,000,000"
}
```

Notes & limitations

- This scraper parses CoinMarketCap's public HTML. If the site changes structure, the parser may break.
- Avoid frequent automated requests; prefer official APIs (CoinMarketCap API, CoinGecko, Coinbase) for production use.
- Error handling in the code is minimal; consider adding timeouts, retries, logging, and clearer exceptions.

Suggested next steps I can implement

- Add a CLI entrypoint that accepts a coin slug and prints JSON.
- Add unit tests with mocked HTTP responses.
- Update `requirements.txt` to pin dependency versions (e.g. `requests==2.31.0`, `beautifulsoup4==4.12.2`).

Author / Contact

faizan code — thetriquetradeveloper@gmail.com

If you want one of the suggested enhancements, tell me which and I'll implement it.
