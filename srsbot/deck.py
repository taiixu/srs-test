from apkg.convert import convert
import os
import time
import random

class SimpleDeck:
    def __init__(self, path):
        self.deck_path = path
        self.__csv_file = open(path, 'r', encoding='utf-8').read()
        self.headers = self.__csv_file.split('\n')[0].split(',')
        self.fields = self.__csv_file.split('\n')[1:-1] if self.__csv_file.split('\n')[-1] == '' else self.__csv_file.split('\n')[1:]
        if not self.check_fields():
            self.add_deck_fields()

    def add_deck_fields(self):
        self.headers += ',___time,___status,___selected_fields'
        for c in range(len(self.fields)):
            self.fields[c] += ',,,'

    def check_fields(self):
        return '___time' in self.headers and '___status' in self.headers and '___selected_fields' in self.headers
    
    def add_selected_fields(self, question, answer):
        self.fields[0] += f'{question};{answer}'
    
    def get_fields(self):
        ret = {}
        for key, index in zip(self.headers[:-3], range(len(self.headers[:-3]))):
            column = []
            for item in self.fields:
                column.append(item.split(',')[index])
            ret.update({key: column})
            column = []
        return ret
    
    def save(self):
        f = open(self.deck_path, 'w', encoding='utf-8')
        f.write(','.join(self.headers) + '\n')
        f.write('\n'.join(self.fields))
        f.close()


class Deck:
    '''
    Statuses:
    1 - new (today)
    2 - studying
    3 - studyed
    '''
    def __init__(self, path):
        self.deck_path = path
        self.__csv_file = open(path, 'r', encoding='utf-8').read()
        self.new_count = 15
        self.headers = self.__csv_file.split('\n')[0].split(',')
        self.fields = self.__csv_file.split('\n')[1:-1] if self.__csv_file.split('\n')[-1] == '' else self.__csv_file.split('\n')[1:]
        if not self.check_fields():
            self.add_deck_fields()
            self.save()
        self.selected_question = self.fields[0][-1].split(';')[0]
        self.selected_answer = self.fields[0][-1].split(';')[1]

    def get_studying_cards(self):
        day_now = int(time.time()) // (24 * 60 * 60)
        
    def get_studying_count(self):
        pass
        

    def get_column(self, field_name):
        index = self.headers.index(field_name)
        ret = []
        for c in self.fields:
            ret.append(c.split(',')[index])
        return ret

    def add_deck_fields(self):
        self.headers += ',___time,___status,___selected_fields'
        for c in range(len(self.fields)):
            self.fields[c] += ',,,'

    def check_fields(self):
        return '___time' in self.headers and '___status' in self.headers and '___selected_fields' in self.headers
    
    def save(self):
        f = open(self.deck_path, 'w', encoding='utf-8')
        f.write(','.join(self.headers) + '\n')
        f.write('\n'.join(self.fields))
        f.close()