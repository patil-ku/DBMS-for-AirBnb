class User:
    logged_in_status = False
    username = None

    def __init__(self):
        self.logged_in_status = False
        self.username = None

    def set_logged_status(self, boolean):
        self.logged_in_status = boolean

    def set_username(self, username):
        self.username = username

    def is_logged_in(self):
        return self.logged_in_status

    def get_username(self):
        return self.username
