import telebot
import os
import sys
import json
from srsbot.handler import MessageHandler
from srsbot.lang import Language
from srsbot.db import DataBase

token = os.environ.get('TOKEN')
if token == None:
    print("Set the telegram token to environment variables")
    sys.exit(-1)

bot = telebot.TeleBot(token)

config = json.loads(open('config.json', 'r', encoding='utf-8').read())

database = DataBase(config['database_path'])

langs = []
for language in os.listdir(config['language_path']):
    l = Language(f"{config['language_path']}/{language}")
    langs.append(l)

handler = MessageHandler(database, langs, bot)

@bot.message_handler(commands=['start'])
def start(message):
    handler.handle(message)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    handler.handle(message)

bot.infinity_polling()