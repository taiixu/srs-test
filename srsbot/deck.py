from apkg.convert import convert
import os
import time
import random

class SimpleDeck:
    def __init__(self, path):
        self.deck_path = path
        self.deck_name = '.'.join(os.path.basename(path).split('.')[:-1])
        self.__csv_file = open(path, 'r', encoding='utf-8').read()
        self.selected_fields = ''
        self.new_count = 15
        self.headers = self.__csv_file.split('\n')[0].split(',')
        self.fields = self.__csv_file.split('\n')[1:-1] if self.__csv_file.split('\n')[-1] == '' else self.__csv_file.split('\n')[1:]
        if not self.check_fields():
            self.add_deck_fields()
        
        self.___time = []
        self.___status = []
        self.add_time()

    def add_deck_fields(self):
        self.headers += ['___time', '___status', '___srs_time', '___card_time']
        for c in range(len(self.fields)):
            self.fields[c] += ',,,,'

    def get_fields(self):
        ret = {}
        for key, index in zip(self.headers[:-4], range(len(self.headers[:-4]))):
            column = []
            for item in self.fields:
                column.append(item.split(',')[index])
            ret.update({key: column})
            column = []
        return ret

    def check_fields(self):
        return '___time' in self.headers and '___status' in self.headers and '___srs_time' in self.headers and '___card_time' in self.headers
    
    def add_selected_fields(self, question, answer):
        self.selected_fields = f'{question};{answer}'
     
    def get_current_day(self):
        return int(time.time()) // (24 * 60 * 60)

    def get_column(self, field_name):
        index = self.headers.index(field_name)
        ret = []
        for c in self.fields:
            ret.append(c.split(',')[index])
        return ret
    
    def add_time(self):
        current_day = self.get_current_day()
        self.___time = self.get_column('___time')
        self.___status = self.get_column('___status')
        for c in range(0, len(self.___time), self.new_count):
            for t in range(c, c+15):
                if t >= len(self.___time):
                    break
                self.___time[t] = str(current_day)
                self.___status[t] = '1'
            current_day += 1
        
    def save(self):
        f = open(self.deck_path, 'w', encoding='utf-8')
        f.write(self.selected_fields + '\n')
        f.write(','.join(self.headers) + '\n')
        # f.write('\n'.join(self.fields))
        for i in range(len(self.fields)):
            f.write(f"{','.join(self.fields[i].split(',')[:-4])},{self.___time[i]},{self.___status[i]},0,0\n")
        f.close()


class Deck:
    '''
    Statuses:
    1 - new (today)
    2 - studying
    3 - studyed

    spaced reprepetition formula: y = int(2,5 * x + 1)
    if answer is incorrect: y = y // 2
    '''
    def __init__(self, path):
        self.deck_path = path
        self.deck_name = '.'.join(os.path.basename(path).split('.')[:-1])
        self.deck_name_without_id = self.deck_name.split(';', maxsplit=1)[1]
        self.__csv_file = open(path, 'r', encoding='utf-8').read()
        self.new_count = 15
        self.__qa = self.__csv_file.split('\n')[0].split(';')
        self.selected_question = self.__qa[0]
        self.selected_answer = self.__qa[1]

        self.headers = self.__csv_file.split('\n')[1].split(',')
        self.fields = self.__csv_file.split('\n')[2:-1] if self.__csv_file.split('\n')[-1] == '' else self.__csv_file.split('\n')[2:]
        if not self.check_fields():
            self.add_deck_fields()
            self.save()

        self.day_now = self.get_current_day()

        self.questions = self.get_column(self.selected_question)
        self.answers = self.get_column(self.selected_answer)
        self.___time = self.get_column('___time')
        self.___status = self.get_column('___status')
        self.___srs_time = self.get_column('___srs_time')
        self.___card_time = self.get_column('___card_time')

        self.new, self.study_now, self.repeat = self.get_studying_cards()
        self.queue = self.list_sum(self.new, self.study_now, self.repeat)
        self.count = self.get_studying_count()
        self.current_card = 0

    def move_to_center(self):
        if len(self.queue) == 1:
            return self.queue
        center_of_list = len(self.queue) // 2
        ret = self.queue[1:center_of_list] + [self.queue[0]] + self.queue[center_of_list:]
        return ret

    def get_new(self, count):
        ret = []
        counter = 0
        for i in range(len(self.questions)):
            if self.___status[i] == '':
                self.___status[i] = '1'
                self.___time[i] = str(self.day_now)
                self.___srs_time[i] = '0'
                self.___card_time[i] = '0'
                ret.append(i)
                counter += 1
            
            if counter == count:
                break
        return ret

    def get_random_answers(self, count, correct_answer):
        if len(self.answers) <= count:
            return None
        ret = []
        while True:
            answer = random.choice(self.answers)
            if answer != correct_answer and answer not in ret:
                ret.append(answer)
            if len(ret) == count:
                break
        return ret
    
    def shuffle_answers(self, correct_answer, incorrect_answers):
        l = [correct_answer] + incorrect_answers
        ret = []
        while len(l) != 0:
            index = random.randint(0, len(l) - 1)
            ret.append(l[index])
            del l[index]
        return ret

    def answer(self, ans):
        if self.answers[self.current_card] == ans:
            if self.___status[self.current_card] == '1':
                self.___status[self.current_card] = '2'
                self.queue = self.move_to_center()
                return True
            self.___status[self.current_card] = '3'
            self.___srs_time[self.current_card] = str(int(2.5 * int(self.___card_time[self.current_card]) + 1))
            self.___card_time[self.current_card] = '0'
            self.___time[self.current_card] = str(self.get_current_day())
            del self.queue[0]
            return True
        else:
            self.___status[self.current_card] = '2'
            self.___srs_time[self.current_card] = str(int(self.___srs_time[self.current_card]) // 2)
            self.queue = self.move_to_center()
            return False
        
    def study(self):
        if len(self.queue) == 0:
            return None
        # self.update()
        self.current_card = self.queue[0]
        question = self.questions[self.current_card]
        answer = self.answers[self.current_card]
        rand_answers = self.get_random_answers(3, answer)
        if rand_answers == None:
            raise Exception("get_random_answers count >= len(answers)")
        return [question, answer, self.shuffle_answers(answer, rand_answers), self.get_studying_count()]
        
    def get_studying_cards(self):
        self.day_now = self.get_current_day()

        new = []
        studying = []
        repeat = []

        for i in range(len(self.questions)):
            if self.___time[i] != '' and self.___status[i] != '' and self.___srs_time[i] != '' and self.___card_time[i] != '':
                if self.___status[i] == '1' and int(self.___time[i]) <= self.day_now:
                    new.append(i)
                elif self.___status[i] == '2':
                    studying.append(i)
                elif self.___status[i] == '3':
                    if int(self.___time[i]) != self.day_now:
                        self.___time[i] = str(self.day_now)
                        self.___card_time[i] = str(int(self.___card_time[i]) + 1)
                    
                if int(self.___card_time[i]) >= int(self.___srs_time[i]) and self.___status[i] == '3':
                    repeat.append(i)
                    self.___status[i] = '2'

        if len(new) != self.new_count:
            n = self.get_new(self.new_count - len(new))
            for c in n:
                new.append(c)
        
        return new, studying, repeat
        
    def get_current_day(self):
        return int(time.time()) // (24 * 60 * 60)

    def get_studying_count(self):
        ret = [0, 0, 0]
        for i in self.queue:
            try:
                status = self.___status[i]
            except:
                break
            if status == '1':
                ret[0] += 1
            elif status == '2':
                ret[1] += 1
            elif status == '3':
                ret[2] += 1
        return ret
        # return len(self.new), len(self.study_now), len(self.repeat)

    def list_sum(self, l1, l2, l3):
        ret = []
        max_list = len(max(l1, l2, l3))
        for i in range(max_list):
            if len(l1) > i:
                ret.append(l1[i])
            if len(l2) > i:
                ret.append(l2[i])
            if len(l3) > i:
                ret.append(l3[i])
        return ret

    def get_column(self, field_name):
        index = self.headers.index(field_name)
        ret = []
        for c in self.fields:
            ret.append(c.split(',')[index])
        return ret

    def add_deck_fields(self):
        # self.headers += ',___time,___status,___srs_time,___card_time'
        self.headers += ['___time', '___status', '___srs_time', '___card_time']
        for c in range(len(self.fields)):
            self.fields[c] += ',,,,'

    def check_fields(self):
        return '___time' in self.headers and '___status' in self.headers and '___srs_time' in self.headers and '___card_time' in self.headers
    
    def add_selected_fields(self, question, answer):
        self.selected_question = question
        self.selected_answer = answer
    
    def get_fields(self):
        ret = {}
        for key, index in zip(self.headers[:-4], range(len(self.headers[:-4]))):
            column = []
            for item in self.fields:
                column.append(item.split(',')[index])
            ret.update({key: column})
            column = []
        return ret

    def update_deck(self):
        self.new, self.study_now, self.repeat = self.get_studying_cards()
        self.queue = self.list_sum(self.new, self.study_now, self.repeat)
        self.count = self.get_studying_count()

    def save(self):
        f = open(self.deck_path, 'w', encoding='utf-8')
        f.write(f'{self.selected_question};{self.selected_answer}\n')
        f.write(','.join(self.headers) + '\n')
        for i in range(len(self.fields)):
            f.write(f"{','.join(self.fields[i].split(',')[:-4])},{self.___time[i]},{self.___status[i]},{self.___srs_time[i]},{self.___card_time[i]}\n")
        f.close()