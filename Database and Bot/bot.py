import time
import telebot
from telegraph import Telegraph
from schedule import every, repeat, run_pending
import os
from dotenv import load_dotenv

import work_with_news

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
graph_token = os.getenv("graph_token")
channel_id = os.getenv("channel_id")

telegraph = Telegraph(graph_token)
bot = telebot.TeleBot(TOKEN)


def new_post(data: list[dict]) -> None:
    for news in data:
        message = "*" + news['title'] + '*\n\n'
        message += news['annot'] + '\n\n'
        vip_persons = ", ".join(news['persons'])
        if len(vip_persons) > 0:
            message += f'VIP-персоны: {vip_persons}' + '\n\n'
        vip_places = ", ".join(news['places'])
        if len(vip_places) > 0:
            message += f'Достопримечательности: {vip_places}' + '\n\n'
        sentiment = news['sentiment']
        if len(sentiment) > 0:
            message += f'Тональность: {sentiment}' + '\n\n'
        response = telegraph.create_page(
            news['title'],  # заголовок страницы
            html_content=news['text']
        )
        telegraph_link = 'https://telegra.ph/{}'.format(response['path'])
        message += f'[Читать новость]({telegraph_link})' + '\n'
        news_link = news['link']
        message += f'[Источник]({news_link})'

        bot.send_message(channel_id, message, parse_mode='Markdown')


@repeat(every(10).seconds)
def make_new_posts():
    try:
        found_news = reversed(work_with_news.get_new_news())
        new_post(found_news)
    except Exception as ex:
        print(ex)


def main():  # в мэйн аргументом передай и все
    # arr = [{"title": "test",
    #         "annot": "test, test",
    #         "text": "XD",
    #         "link": "https://pornhub.com",
    #         "persons": "Nikon",
    #         "places": "Общажитие №3",
    #         "sentiment": "zaebis"}]
    while True:
        run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
