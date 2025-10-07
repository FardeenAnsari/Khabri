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
    "https://dl.flipkart.com/s/V7zBMvuuuN",  # Replace with your product URLs
    # Add more URLs if needed
]

def get_price(url):
    """Fetch current price from Amazon."""
    headers = {"User-Agent": "Mozilla/5.0"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    price_tag = soup.find("span", {"class": "a-price-whole"})
    if not price_tag:
        return "Price not found"
    return price_tag.text.strip()

def send_price_update():
    """Send hourly price update for all products."""
    message = "📰 *Khabri Update!*\n\n"
    for url in PRODUCTS:
        price = get_price(url)
        message += f"Product: {url}\nPrice: ₹{price}\n\n"
    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

# --- Main loop: runs every hour ---
while True:
    try:
        send_price_update()
        print("Sent hourly update!")
    except Exception as e:
        print("Error:", e)
    time.sleep(3600)  # Wait 1 hour
