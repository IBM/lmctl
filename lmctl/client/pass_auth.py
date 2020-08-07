from .auth import Auth

class UserPassAuth(Auth):

    def __init__(self, username: str, password: str, client_id: str, client_secret: str):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

class LegacyUserPassAuth(Auth):

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password