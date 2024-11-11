from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from .db import DataBase

class UserBase:
    def __init__(self, base: DataBase) -> None:
        self.base = base
        self.__user_list = []
        self.__upload_from_db()

    def add_user(self, user):
        self.__user_list.append(user)

    def update_db(self):
        pass

    def __upload_from_db(self):
        pass

    def is_user_exist(self, user_id):
        for usr in self.__user_list:
            if usr.user_id == user_id:
                return True
        return False

class User:
    def __init__(self, uid, bot, languages: list):
        self.stage = "setup:0"
        self.user_id = uid
        self.languages = languages
        self.lang = self.languages[0]
        self.decks = []
        self.__bot = bot
    
    def __keyboard_setup_lang(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        [markup.add(c.name) for c in self.languages]
        return markup
    
    def __keyboard_main_menu(self):
        pass

    def setup(self):
        self.__bot.send_message(self.user_id, self.lang.print("languageSetup"), reply_markup=self.__keyboard_setup_lang())

    def handle_message(self, message):
        if self.stage == "setup:0":
            self.__bot.send_message(self.user_id, self.lang.print("welcome"), reply_markup=self.__keyboard_main_menu())
        
