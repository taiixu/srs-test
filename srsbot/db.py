import json
from user import User

class DataBase:
    def __init__(self, path):
        self.path = path
        self.__database = json.loads(open(path, 'r', encoding='utf-8').read())

    def __update(self):
        open(self.path, 'w', encoding='utf-8').write(json.dumps(self.__database))

    def create_user(self, uid, lang):
        if uid in self.__database.keys():
            raise Exception("User already in database")
        self.__database.update({
            uid: {
                "lang": lang,
                "decks": [],
                "stage": "main",
            }
        })
        self.__update()
    
    def update_user(self, uid, lang, decks, stage):
        self.__database.update({
            uid: {
                "lang": lang,
                "decks": decks,
                "stage": stage
            }
        })
        self.__update()

    def get_stage(self, uid):
        return self.__database[uid]['stage']

    def set_stage(self, uid, stage):
        self.__database[uid]['stage'] = stage
        self.__update()
    
    def add_deck(self, uid, deck_name, q_field, a_field):
        self.__database[uid]['decks'].append([deck_name, q_field, a_field])
        self.__update()
    
    def remove_deck(self, uid, deck_name):
        for c, deck in zip(range(len(self.__database[uid]['decks'])), self.__database[uid]['decks']):
            if deck[0] == deck_name:
                del self.__database[uid]['decks'][c]
        self.__update()
    
    def get_decks(self, uid):
        return self.__database[uid]['decks']
    
    def inDatabase(self, uid):
        return uid in self.__database