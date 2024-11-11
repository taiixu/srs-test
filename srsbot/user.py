class UserBase:
    def __init__(self, base) -> None:
        self.base = base
        self.user_list = []
        self.__upload_from_db()

    def add_user(self, user):
        pass

    def update_db(self):
        pass

    def __upload_from_db(self):
        pass

    def is_user_exist(self, user_id):
        pass

class User:
    def __init__(self, uid):
        self.stage = "setup"
        self.user_id = uid
        self.languages = []
        self.selected_language = "en"
        self.decks = []
    
    def setup(self):
        pass
    
    
