import telebot
import os
import sys

token = os.environ.get('TOKEN')
if token == None:
    print("Set the telegram token to environment variables")
    sys.exit(-1)

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "hello world")

bot.infinity_polling()