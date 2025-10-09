# bot.py
import os
import time
import requests
import re
from bs4 import BeautifulSoup
from telegram import Bot

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PRODUCTS = os.getenv("PRODUCTS", "")  # comma-separated URLs

if not BOT_TOKEN or not CHAT_ID or not PRODUCTS:
    print("ERROR: BOT_TOKEN, CHAT_ID or PRODUCTS environment variable missing.")
    raise SystemExit(1)

bot = Bot(token=BOT_TOKEN)
urls = [u.strip() for u in PRODUCTS.split(",") if u.strip()]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}

def fetch_price(url):
    """Fetch the current price of a product from Flipkart or Amazon."""
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # --- Flipkart: current discounted price ---
            fp = soup.select_one("div.Nx9bqj.CxhGGd")
            if fp:
                raw_price = fp.get_text(strip=True)
                print(f"[DEBUG] Raw price for {url}: {raw_price}")
                val = re.sub(r"[^\d]", "", raw_price)  # keep digits only
                if val:
                    return val

            # --- Other selectors (Amazon or fallback) ---
            selectors = [
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                "span.a-price-whole",
                "span.a-offscreen",
                "meta[itemprop=price]"
            ]
            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    txt = el.get("content") if el.name == "meta" else el.get_text(strip=True)
                    val = re.sub(r"[^\d]", "", txt)
                    if val:
                        return val

            return "Price not found"

        except Exception as e:
            print(f"[try {attempt}] Error fetching {url}: {e}")
            time.sleep(2)

    return "Error fetching after retries"

def build_message(urls):
    parts = ["Khabri hourly price update:"]
    for u in urls:
        price = fetch_price(u)
        parts.append(f"{u}\nPrice: ₹{price}")
    return "\n\n".join(parts)

def main():
    msg = build_message(urls)
    print("Message to send:\n", msg)
    try:
        bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
        print("Telegram message sent.")
    except Exception as e:
        print("Error sending Telegram message:", e)
        raise

if __name__ == "__main__":
    main()
