import datetime
import logging
import time

logger = logging.getLogger(__name__)

class AuthTracker:

    def __init__(self):
        self.current_access_token = None
        self._access_expiration = None
        self.time_of_auth = None

    @property
    def has_access_expired(self):
        if self.current_access_token is None:
            logger.debug('No current access token, must request one')
            return True
        logger.debug('Checking if LM access token has expired')
        now = datetime.datetime.now()
        time_with_access = (now - self.time_of_auth).total_seconds()
        logger.debug(f'Authenticated {time_with_access} seconds ago, token has an expiration time of {self._access_expiration} seconds')
        if time_with_access >= self._access_expiration:
            logger.debug('Token expired, must request a new one')
            return True
        # If the token expires within 1 second, wait and get a new one
        if time_with_access >= (self._access_expiration-1):
            logger.debug('Expires in less than 1 second, must request a new one')
            time.sleep(1)
            return True
        return False
    
    def accept_auth_response(self, auth_response):
        self.time_of_auth = datetime.datetime.now()
        self.current_access_token = auth_response.get('access_token', auth_response.get('accessToken'))
        self._access_expiration = auth_response.get('expires_in', auth_response.get('expiresIn'))