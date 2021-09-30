from datetime import datetime, timedelta
import logging
import time
import jwt
import os

logger = logging.getLogger(__name__)

class AuthTracker:

    def __init__(self):
        self.current_access_token = None
        self.time_of_auth = None # Datetime obj of when we're authenticated
        self._time_of_expiry = None # Datetime obj of when the current token expires
        tmp_jwt_algo = os.environ.get('LM_JWT_ALGO', None)
        if tmp_jwt_algo is None or len(tmp_jwt_algo.strip()) == 0:
            tmp_jwt_algo = ['HS256', 'HS384', 'HS512']
        else:
            tmp_jwt_algo = tmp_jwt_algo.split(',')
        self.jwt_algorithms = tmp_jwt_algo

    @property
    def has_access_expired(self):
        if self.current_access_token is None:
            logger.debug('No current access token, must request one')
            return True
        logger.debug('Checking if CP4NA orchestration access token has expired')
        now = datetime.now()
        logger.debug(f'Authenticated at {self.time_of_auth.isoformat()}, the time is {now.isoformat()}, token has an expiration timestamp of {self._time_of_expiry.isoformat()}')
        if now >= self._time_of_expiry:
            logger.debug('Token expired, must request a new one')
            return True
        # If the token expires within 3/4 of a second, wait and get a new one
        if now + timedelta(seconds = 0.75) >= self._time_of_expiry:
            logger.debug('Expires in less than 1 second, must request a new one')
            time.sleep(0.75)
            return True
        return False
    
    def accept_auth_response(self, auth_response):
        self.time_of_auth = datetime.now()
        if 'token' in auth_response:
            self.current_access_token = auth_response.get('token')
            self._time_of_expiry = self._get_expires_time_from_jwt(self.current_access_token)
        else:
            self.current_access_token = auth_response.get('access_token', auth_response.get('accessToken'))
            self._time_of_expiry = self._get_expires_time_from_jwt(self.current_access_token)

    def _get_expires_time_from_jwt(self, token):
        jwt_content = jwt.decode(token, options={'verify_signature': False, 'verify_aud': False}, algorithms=self.jwt_algorithms)
        exp = jwt_content.get('exp')
        if exp is None:
            raise ValueError('Expected "exp" in token content')
        return datetime.fromtimestamp(exp)