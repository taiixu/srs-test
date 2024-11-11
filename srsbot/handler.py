from .user import User, UserBase

class MessageHandler:
    def __init__(self, db):
        self.database = db
        self.languages = []
        self.user_base = UserBase(self.database)
    
    def handle(self, message):
        if not self.user_base.is_user_exist(message.chat.id):
            user = User()