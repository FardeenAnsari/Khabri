import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# --- Telegram Bot setup ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=BOT_TOKEN)

# --- Product URLs to track ---
PRODUCTS = [
    "https://dl.flipkart.com/s/V7zBMvuuuN",  # Replace with actual product URLs
    # Add more URLs if needed
]

def get_price_flipkart(url):
    """Fetch current price from Flipkart."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/116.0.0.0 Safari/537.36"
    }
    try:
        page = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(page.text, "html.parser")
        # Flipkart price span selector
        price_tag = soup.find("div", {"class": "_30jeq3 _16Jk6d"})
        if not price_tag:
            return "Price not found"
        # Remove non-numeric characters
        price = price_tag.text.strip().replace("₹", "").replace(",", "")
        return price
    except Exception as e:
        return f"Error fetching price: {e}"

def send_price_update():
    """Send hourly price update for all products."""
    message = "📰 *Khabri Update!*\n\n"
    for url in PRODUCTS:
        price = get_price_flipkart(url)
        message += f"Product: {url}\nPrice: ₹{price}\n\n"
    try:
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")
    except Exception as e:
        print("Error sending message:", e)

# --- Main loop: runs every hour ---
while True:
    send_price_update()
    print("Sent hourly update!")
    time.sleep(3600)  # Wait 1 hour
