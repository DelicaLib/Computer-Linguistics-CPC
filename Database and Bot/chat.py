import telebot
import os
from dotenv import load_dotenv

import work_with_news

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Напишите слово, что бы получить синоним", parse_mode='Markdown')


@bot.message_handler()
def synonym(message):
    word = message.text  # вот тут слово
    words = work_with_news.get_synonyms(word)
    if len(words):
        bot.send_message(message.chat.id, "\n".join(words), parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Не удалось подобрать синонимы", parse_mode='Markdown')


bot.polling(non_stop=True)
