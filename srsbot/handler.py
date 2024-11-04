from .user import User
from .db import DataBase

users = {}

class MessageHandler:
    def __init__(self, db):
        self.database = db
    
    def handle(self, message):
        if message.chat.id not in users and not self.database.inDatabase(message.chat.id):
            pass