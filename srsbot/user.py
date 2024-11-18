from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from .db import DataBase
import os
from apkg.convert import convert as apkg_convert
from .deck import SimpleDeck, Deck
import traceback

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
            deck_names = [c.deck_name for c in usr.decks]
            self.base.update_user(str(usr.user_id), usr.lang.key, deck_names, usr.stage)

    def __upload_from_db(self):
        raw_db = self.base.get_db()
        for uid in raw_db:
            u_info = raw_db[uid]
            user = User(int(uid), self.bot, self.langs, self.decks_path, self.temp_path)
            user.stage = u_info['stage']
            user.languages = self.langs
            for l in self.langs:
                if l.key == u_info['lang']:
                    user.lang = l
                    user.lang_name = l.name
            user.decks = []
            for deck in u_info['decks']:
                user.decks.append(Deck(f"{self.decks_path}/{deck}.csv"))
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
        self.fields = None
        self.fields_list = None
        self.question = ''
        self.answer = ''

        self.studying_deck = None
        self.current_question = None
        
        self.current_setting_deck_index = None
    
    def __sentence_short(self, text, length=40):
        if len(text) < length:
            return text
        else:
            return text[:40] + '...'

    def __text_deck_fields(self):
        ret = ''
        for key, value in zip(self.fields.keys(), self.fields.values()):
            ret += f"{key}: {self.__sentence_short(', '.join(value))}\n\n"
        return ret[:-2]
    
    def __keyboard_setup_lang(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        [markup.add(KeyboardButton(c.name)) for c in self.languages]
        return markup
    
    def __keyboard_main_menu(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        for c in self.decks:
            markup.add(c.deck_name_without_id)
        add_deck = KeyboardButton(self.lang.print("buttonAddDeck"))
        settings = KeyboardButton(self.lang.print("buttonSettings"))
        markup.add(add_deck, settings)
        return markup
    
    def __keyboard_back_button(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        back_button = KeyboardButton(self.lang.print("buttonBack"))
        markup.add(back_button)
        return markup

    def __keyboard_deck_fields(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        for c in self.fields:
            markup.add(KeyboardButton(c))
        return markup
    
    def __keyboard_settings_setup_lang(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        [markup.add(KeyboardButton(c.name)) for c in self.languages]
        back_button = KeyboardButton(self.lang.print("buttonBack"))
        markup.add(back_button)
        return markup
    
    def __keyboard_main_settins(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        decks_button = KeyboardButton(self.lang.print("buttonDecksSettings"))
        lang_button = KeyboardButton(self.lang.print("buttonLanguageSettings"))
        back_button = KeyboardButton(self.lang.print("buttonBack"))
        markup.add(decks_button, lang_button, back_button)
        return markup
    
    def __keyboard_settings_decks(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        for c in self.decks:
            markup.add(KeyboardButton(c.deck_name_without_id))
        back_button = KeyboardButton(self.lang.print("buttonBack"))
        markup.add(back_button)
        return markup
    
    def __keyboard_settings_deck_menu(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        change_fields_button = KeyboardButton(self.lang.print("buttonChangeFields"))
        remove_deck_button = KeyboardButton(self.lang.print("buttonRemoveDeck"))
        back_button = KeyboardButton(self.lang.print("buttonBack"))
        markup.add(change_fields_button, remove_deck_button, back_button)
        return markup
    
    def __keyboard_yes_or_no(self):
        markup = ReplyKeyboardMarkup(row_width=1)
        yes = KeyboardButton(self.lang.print("buttonYes"))
        no = KeyboardButton(self.lang.print("buttonNo"))
        markup.add(yes, no)
        return markup

    def send_question(self, status=None):
        prefix = ''
        if status == False:
            prefix = f"{self.lang.print("incorrectAnswer")}{self.current_question[1]}"
        elif status == True:
            prefix = f"{self.lang.print("correctAnswer")}"
        try:
            self.current_question = self.studying_deck.study()
        except:
            print(traceback.format_exc())
            self.stage = "main"
            self.send("interrupt", self.__keyboard_main_menu())
            return
        if self.current_question == None:
            self.stage = "main"
            self.send("endStudy", self.__keyboard_main_menu())
            self.studying_deck.save()
            return
        markup = ReplyKeyboardMarkup()
        for c in self.current_question[2]:
            markup.add(KeyboardButton(c))
        markup.add(self.lang.print("buttonBack"))
        self.studying_deck.save()
        self.__bot.send_message(self.user_id, f"{prefix}\n{self.current_question[0]}\n\n{'/'.join([str(c) for c in self.current_question[3]])}", reply_markup=markup)

    def setup(self):
        self.__bot.send_message(self.user_id, self.lang.print("languageSetup"), reply_markup=self.__keyboard_setup_lang())

    def send(self, msg, keyboard, send_after=''):
        self.__bot.send_message(self.user_id, self.lang.print(msg) + send_after, reply_markup=keyboard)
    
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
                print(traceback.format_exc())
                self.send_w_keyboard("uploadError")
                return
            
            try:
                self.add_deck_edit = SimpleDeck(f"{self.decks_path}/{self.user_id};{'.'.join(filename.split('.')[:-1])}.csv")
            except:
                print(traceback.format_exc())
                self.send_w_keyboard("uploadError")
                return
            self.stage = "deck_add:fields_edit:q"
            self.fields = self.add_deck_edit.get_fields()
            self.fields_list = list(self.fields.keys())

            self.send("deckUploadQuestionChoose", self.__keyboard_deck_fields(), send_after=f'\n{self.__text_deck_fields()}')
        elif self.stage == 'deck_add:fields_edit:q':
            if message.text not in self.fields_list:
                self.send_w_keyboard("keyWrong")
                return
            self.question = message.text
            self.stage = "deck_add:fields_edit:a"
            self.send("deckUploadAnswerChoose", self.__keyboard_deck_fields(), send_after=f'\n{self.__text_deck_fields()}')
        elif self.stage == "deck_add:fields_edit:a":
            if message.text not in self.fields_list:
                self.send_w_keyboard("keyWrong")
                return
            self.answer = message.text
            self.add_deck_edit.add_selected_fields(self.question, self.answer)
            self.add_deck_edit.save()
            self.decks.append(Deck(self.add_deck_edit.deck_path))
            self.stage = "main"
            self.send("deckAddSuccess", self.__keyboard_main_menu())
        elif self.stage == "main" and message.text in [c.deck_name_without_id for c in self.decks]:
            for c in self.decks:
                if c.deck_name_without_id == message.text:
                    self.studying_deck = c
            if len(self.studying_deck.queue) == 0:
                self.send_w_keyboard("deckStudied")
                return
            self.stage = 'deck_study'
            self.studying_deck.update_deck()
            self.send_question()
        elif self.stage == "deck_study" and message.text in self.current_question[2]:
            isCorrect = self.studying_deck.answer(message.text)
            self.send_question(status=isCorrect)
        elif self.stage == "deck_study" and message.text == self.lang.print("buttonBack"):
            self.stage = "main"
            self.send("mainMenu", self.__keyboard_main_menu())
        elif self.stage == "main" and message.text == self.lang.print("buttonSettings"):
            self.stage = "settings:main"
            self.send("settings", self.__keyboard_main_settins())
        elif self.stage == "settings:main" and message.text == self.lang.print("buttonBack"):
            self.stage = "main"
            self.send("mainMenu", self.__keyboard_main_menu())
        elif self.stage == "settings:main" and message.text == self.lang.print("buttonLanguageSettings"):
            self.stage = "settings:language"
            self.send("languageSetup", self.__keyboard_settings_setup_lang())
        elif self.stage == "settings:language" and message.text in [c.name for c in self.languages]:
            self.lang = self.languages[[c.name for c in self.languages].index(message.text)]
            self.stage = "settings:main"
            self.send("langChoose", self.__keyboard_main_settins(), send_after=self.lang.name)
        elif self.stage == "settings:language" and message.text == self.lang.print("buttonBack"):
            self.stage = "settings:main"
            self.send("settings", self.__keyboard_main_settins())
        elif self.stage == "settings:main" and message.text == self.lang.print("buttonDecksSettings"):
            self.stage = "settings:decks_edit"
            self.send("decksSettings", self.__keyboard_settings_decks())
        elif self.stage == "settings:decks_edit" and message.text == self.lang.print("buttonBack"):
            self.stage = "settings:main"
            self.send("settings", self.__keyboard_main_settins())
        elif self.stage == "settings:decks_edit" and message.text in [c.deck_name_without_id for c in self.decks]:
            self.current_setting_deck_index = [c.deck_name_without_id for c in self.decks].index(message.text)
            self.stage = "settings:decks_edit:menu"
            self.send("choosedDeckSettings", self.__keyboard_settings_deck_menu(), send_after=self.decks[self.current_setting_deck_index].deck_name_without_id)
        elif self.stage == "settings:decks_edit:menu" and message.text == self.lang.print("buttonBack"):
            self.stage = "settings:decks_edit"
            self.send("decksSettings", self.__keyboard_settings_decks())
        elif self.stage == "settings:decks_edit:menu" and message.text == self.lang.print("buttonChangeFields"):
            self.fields = self.decks[self.current_setting_deck_index].get_fields()
            self.stage = "settings:decks_edit:fields:q"
            self.send("deckUploadQuestionChoose", self.__keyboard_deck_fields(), send_after=f'\n{self.__text_deck_fields()}')
        elif self.stage == "settings:decks_edit:fields:q" and message.text in self.fields:
            self.question = message.text
            self.stage = "settings:decks_edit:fields:a"
            self.send("deckUploadAnswerChoose", self.__keyboard_deck_fields(), send_after=f'\n{self.__text_deck_fields()}')
        elif self.stage == "settings:decks_edit:fields:a" and message.text in self.fields:
            self.answer = message.text
            self.decks[self.current_setting_deck_index].add_selected_fields(self.question, self.answer)
            self.decks[self.current_setting_deck_index].save()
            d_path = self.decks[self.current_setting_deck_index].deck_path
            del self.decks[self.current_setting_deck_index]
            self.decks.append(Deck(d_path))
            self.stage = "settings:decks_edit"
            self.send("fieldsChooseSuccess", self.__keyboard_settings_decks())
        elif self.stage == "settings:decks_edit:menu" and message.text == self.lang.print("buttonRemoveDeck"):
            self.stage = "settings:decks_edit:remove"
            self.send("removeDeckSure", self.__keyboard_yes_or_no())
        elif self.stage == "settings:decks_edit:remove" and message.text == self.lang.print("buttonNo"):
            self.stage = "settings:decks_edit:menu"
            self.send("choosedDeckSettings", self.__keyboard_settings_deck_menu(), send_after=self.decks[self.current_setting_deck_index].deck_name_without_id)
        elif self.stage == "settings:decks_edit:remove" and message.text == self.lang.print("buttonYes"):
            os.remove(self.decks[self.current_setting_deck_index].deck_path)
            del self.decks[self.current_setting_deck_index]
            self.stage = "settings:decks_edit"
            self.send("removeSuccess", self.__keyboard_settings_decks())
        else:
            self.send_w_keyboard("keyWrong")
        

