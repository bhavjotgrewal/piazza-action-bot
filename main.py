import asyncio
from piazza_api import Piazza
from telegram.ext import Application
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Piazza credentials
PIAZZA_EMAIL = os.getenv("PIAZZA_EMAIL")
PIAZZA_PASSWORD = os.getenv("PIAZZA_PASSWORD")
PIAZZA_NETWORK_ID = os.getenv("PIAZZA_NETWORK_ID")

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Initialize Piazza
p = Piazza()
p.user_login(email=PIAZZA_EMAIL, password=PIAZZA_PASSWORD)
eco202 = p.network(PIAZZA_NETWORK_ID)

# Initialize Telegram bot
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def send_telegram_message(message):
    await application.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def get_post_info(post):
    history = post['history'][0]
    title = history.get('subject', 'No title')
    content = history.get('content', 'No content')
    return f"New post:\nTitle: {title}\nContent: {content[:200]}..."  # Truncate content to 200 chars

def check_for_new_posts():
    latest_posts = list(eco202.iter_all_posts(limit=1))
    if latest_posts:
        latest_post = latest_posts[0]
        return latest_post
    return None

async def main():
    last_post_id = None
    while True:
        try:
            new_post = check_for_new_posts()
            if new_post and new_post['id'] != last_post_id:
                post_info = get_post_info(new_post)
                await send_telegram_message(post_info)
                last_post_id = new_post['id']
            await asyncio.sleep(30)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            print(error_message)
            await send_telegram_message(error_message)
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())