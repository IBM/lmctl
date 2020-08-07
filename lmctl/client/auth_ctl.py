from .auth import Auth

class AuthController:

    def __init__(self, auth: Auth):
        self.auth = auth