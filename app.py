import os
import requests
import schedule
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")

# NewsAPI URL
news_api_key = os.getenv("NEWS_API_KEY")
news_api_url = f"https://newsapi.org/v2/top-headlines?apiKey={news_api_key}&category=technology&country=us"

# Store the latest 5 news
latest_5_news = []


def get_news():
    try:
        response = requests.get(news_api_url)
        response.raise_for_status()  # Raises an exception if the response is not 200 OK

        news_data = response.json()
        new_news = []

        for article in news_data["articles"]:
            title = article["title"]
            url = article["url"]
            description = article.get("description", "No description available.")
            new_news.append({"title": title, "url": url, "description": description})

        return new_news

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return []
    except Exception as err:
        print(f"An error occurred: {err}")
        return []


def send_news(news):
    if news:
        # Send introductory message
        intro_message = "Here are the latest 5 most relevant technology news!\n\n"
        send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {"chat_id": chat_id, "text": intro_message, "parse_mode": "HTML"}
        try:
            requests.post(send_message_url, params=params)
        except requests.exceptions.RequestException as err:
            print(f"Error sending intro message: {err}")

        # Send each news with its title, description, and URL
        for article in news:
            title = article["title"]
            description = article["description"]
            url = article["url"]
            message = f"<b>{title}</b>\n{description}\n{url}"

            params = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            try:
                requests.post(send_message_url, params=params)
            except requests.exceptions.RequestException as err:
                print(f"Error sending news message: {err}")


def update_latest_news():
    global latest_5_news
    new_news = get_news()

    if new_news:
        latest_5_news = new_news[-5:]
        send_news(latest_5_news)


# Start with the latest 5 news at the beginning
update_latest_news()

# Schedule news update every 5 hours
schedule.every(5).hours.do(update_latest_news)

while True:
    schedule.run_pending()
    time.sleep(1)
