# bot.py
import os
import time
import requests
import re
from bs4 import BeautifulSoup
from telegram import Bot

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

def extract_number(text):
    # return first numeric-like group (e.g. "12,499.00") cleaned to "12499.00"
    if not text:
        return None
    m = re.search(r"[\d,]+(\.\d+)?", text.replace("₹", ""))
    return m.group(0).replace(",", "") if m else None

def fetch_price(url):
    for attempt in range(1, 4):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Flipkart price common selector
            fp = soup.select_one("#container > div > div._39kFie.N3De93.JxFEK3._48O0EI > div.DOjaWF.YJG4Cf > div.DOjaWF.gdgoEp.col-8-12 > div:nth-child(3) > div > div.x\\+7QT1.dB67CR > div.UOCQB1 > div > div.Nx9bqj.CxhGGd")
            if fp:
                val = extract_number(fp.get_text())
                if val:
                    return val

            # Amazon and other selectors
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
                    txt = el.get("content") if el.name == "meta" else el.get_text()
                    val = extract_number(txt)
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
