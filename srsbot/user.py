from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from .db import DataBase
import os
from apkg.convert import convert as apkg_convert
from .deck import SimpleDeck, Deck

class UserBase:
    def __init__(self, base: DataBase, langs: list, bot, decks_path, temp_path) -> None:
        self.base = base
        self.langs = langs
        self.bot = bot
        self.decks_path = decks_path
        self.temp_path = temp_path
        self.__user_list = []
        self.__upload_from_db()

    def add_user(self, user):
        self.__user_list.append(user)

    def update_db(self):
        for usr in self.__user_list:
            self.base.update_user(str(usr.user_id), usr.lang_name, usr.decks, usr.stage)

    def __upload_from_db(self):
        raw_db = self.base.get_db()
        for uid in raw_db:
            u_info = raw_db[uid]
            user = User(int(uid), self.bot, self.langs, self.decks_path, self.temp_path)
            user.stage = u_info['stage']
            user.languages = self.langs
            for l in self.langs:
                if l.name == u_info['lang']:
                    user.lang = l
                    user.lang_name = l.name
            user.decks = u_info['decks'] # TODO: Make deck object
            self.__user_list.append(user)
            
    def is_user_exist(self, user_id):
        for usr in self.__user_list:
            if usr.user_id == user_id:
                return True
        return False
    
    def get_user_by_id(self, user_id):
        for c in self.__user_list:
            if c.user_id == user_id:
                return c

class User:
    def __init__(self, uid, bot, languages: list, decks_path: str, temp_path: str):
        self.stage = "setup:0"
        self.user_id = uid
        self.languages = languages
        self.lang = self.languages[0]
        self.lang_name = self.languages[0].key
        self.decks = []
        self.__bot = bot
        self.decks_path = decks_path
        self.temp_path = temp_path

        self.add_deck_edit = None
    
    def __keyboard_setup_lang(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        [markup.add(KeyboardButton(c.name)) for c in self.languages]
        return markup
    
    def __keyboard_main_menu(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        add_deck = KeyboardButton(self.lang.print("buttonAddDeck"))
        settings = KeyboardButton(self.lang.print("buttonSettings"))
        markup.add(add_deck, settings)
        return markup
    
    def __keyboard_back_button(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        back_button = KeyboardButton(self.lang.print("buttonBack"))
        markup.add(back_button)
        return markup

    def setup(self):
        self.__bot.send_message(self.user_id, self.lang.print("languageSetup"), reply_markup=self.__keyboard_setup_lang())

    def send(self, msg, keyboard):
        self.__bot.send_message(self.user_id, self.lang.print(msg), reply_markup=keyboard)
    
    def send_w_keyboard(self, msg):
        self.__bot.send_message(self.user_id, self.lang.print(msg))

    def handle_message(self, message):
        if self.stage == "setup:0":
            for c in self.languages:
                if c.name == message.text:
                    self.lang = c
                    self.lang_name = c.key
                    break
            else:
                self.send_w_keyboard("keyWrong")
                return
            self.send("welcome", self.__keyboard_main_menu())
            self.stage = "main"
        elif message.text == self.lang.print("buttonAddDeck") and self.stage == "main":
            self.stage = "deck_add"
            self.send("addDeck", self.__keyboard_back_button())
        elif message.text == self.lang.print("buttonBack") and self.stage == "deck_add":
            self.stage = "main"
            self.send("mainMenu", self.__keyboard_main_menu())
        elif self.stage == "deck_add":
            try:
                filename = message.document.file_name
                file_info = self.__bot.get_file(message.document.file_id)
                downloaded_file = self.__bot.download_file(file_info.file_path)
                open(f"{self.temp_path}/{self.user_id};{filename}", "wb").write(downloaded_file)
                apkg_convert(f"{self.temp_path}/{self.user_id};{filename}", f"{self.decks_path}/{self.user_id};{'.'.join(filename.split('.')[:-1])}.csv")
                os.remove(f"{self.temp_path}/{self.user_id};{filename}")
            except:
                self.send_w_keyboard("uploadError")
                return
            
            self.stage = "settings:decks_edit"
            self.add_deck_edit = SimpleDeck(f"{self.decks_path}/{self.user_id};{'.'.join(filename.split('.')[:-1])}.csv")
            
            
