from .user import User, UserBase
from .db import DataBase

class MessageHandler:
    def __init__(self, db: DataBase, languages: list, bot):
        self.database = db
        self.languages = languages
        self.user_base = UserBase(self.database, self.languages, bot)
        self.bot = bot
    
    def handle(self, message):
        if not self.user_base.is_user_exist(message.chat.id):
            user = User(message.chat.id, self.bot, self.languages)
            user.setup()
            self.user_base.add_user(user)
            self.user_base.update_db()
            return
        
        user = self.user_base.get_user_by_id(message.chat.id)
        user.handle_message(message)
        self.user_base.update_db()