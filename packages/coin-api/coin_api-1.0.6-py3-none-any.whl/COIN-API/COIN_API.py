from bs4 import BeautifulSoup
import requests
import sys
import json

price_class = "sc-65e7f566-0 esyGGG base-text"
arrow_class = "sc-71024e3e-0 sc-9e7b7322-1 ihXFUo dXVXKV change-text"
Market_cap_div_class = ".BasePopover_base__T5yOf popover-base span"
header = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
}


class Coin:
    def __init__(self, coin: str):
        """Fetch and parse the CoinMarketCap page for `coin` (slug).

        Args:
            coin: coinmarketcap slug (e.g. "bitcoin", "ethereum").
        """
        if not coin:
            raise ValueError("coin slug required")

        res = requests.get(f"https://coinmarketcap.com/currencies/{coin}/", headers=header, timeout=10)
        res.raise_for_status()
        self.soup = BeautifulSoup(res.text, "html.parser")

    def get_data(self):
        """Return a dict with Price, 24h change and Market cap, or raise on parse error."""
        price_el = self.soup.find(class_=price_class)
        change_el = self.soup.find(class_=arrow_class)
        spans = self.soup.find_all("span")

        if not price_el or not change_el or len(spans) <= 11:
            raise RuntimeError("failed to parse CoinMarketCap HTML; page structure may have changed")

        price_text = price_el.text.strip()
        day_cap = change_el.text.strip()[0:5]
        arrow = "↗️" if change_el.get("color") == "green" else "↘️"
        coin_cap = spans[11].text.strip()

        return {
            "Price": price_text,
            "24h change": f"{day_cap} {arrow}",
            "Market cap": coin_cap,
        }


def main(argv=None):
    """CLI entrypoint: coin slug -> JSON printed to stdout."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        print("Usage: coin-price <coin-slug>", file=sys.stderr)
        return 2

    slug = argv[0]
    try:
        data = Coin(slug).get_data()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(json.dumps(data, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
from bs4 import BeautifulSoup
import requests

price_class = "sc-65e7f566-0 esyGGG base-text"
arrow_class = "sc-71024e3e-0 sc-9e7b7322-1 ihXFUo dXVXKV change-text"
Market_cap_div_class = ".BasePopover_base__T5yOf popover-base span"
header = {
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
class Coin:
     def __init__(self,coin):
        """When you add a name of the coin the function will be setuped for the coin"""
        if coin:
           try:
              res = requests.get(f"https://coinmarketcap.com/currencies/{coin}/",headers=header)
           except:
               print("enter valid name the coin was not valid")
               return False
           self.soup = BeautifulSoup(res.text,"html.parser")

        else:
            print("pls enter a valid value")
     def get_data(self):
          try:
               price = self.soup.find(class_=price_class).text
               day_cap = self.soup.find(class_=arrow_class).text[0:5]
               arrow = "↗️" if self.soup.find(class_=arrow_class).get("color") == "green" else "↘️"
               coin_cap = self.soup.find_all("span")[11].text
               return {
               "Price": price,
               "24h change": f"{day_cap} {arrow}",
               "Market cap": coin_cap
               }
          except:
              print("error occured pls try again later")
              return False
          
         
     
if __name__ == "__main__":
    print(Coin("bitcoin").get_data())
     