import json

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
    
    def get_db(self):
        return self.__database

    def inDatabase(self, uid):
        return uid in self.__database