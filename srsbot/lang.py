import json

class Language:
    def __init__(self, lang):
        self.language_path = lang
        self.__lang_file = json.loads(open(self.language_path, 'r', encoding='utf-8').read())
        self.name = self.__lang_file['languageName']
        self.key = self.__lang_file['languageAbbr']
    
    def print(self, key):
        return self.__lang_file[key]