from distutils.command.build import build
import jwt
from datetime import datetime, timedelta
from lmctl.client import AuthType

def build_a_token(username='JohnDoe', expires_in=30):
    token_content = {
        'sub': '1234567890',
        'username': username,
        'jti': 'c257f98d-f4dd-4fa9-afb4-6329924316f2',
        'iat': int(datetime.now().strftime('%s')),
        'exp': int((datetime.now() + timedelta(seconds=expires_in)).strftime('%s'))
    }
    return jwt.encode(token_content, 'secret', algorithm='HS256')

class FakeTNCOAuth(AuthType):

    def __init__(self, token=None):
        self.token = token or build_a_token()
    
    def handle(self, *args, **kwargs):
        return {
            'token': self.token
        }
    