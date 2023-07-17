import datetime
import requests
import logging
import time
from .base import LmDriver
from lmctl.client import  AuthTracker

logger = logging.getLogger(__name__)


class LmSecurityDriver(LmDriver):
    """
    Client for CP4NA orchestration Security APIs
    """

    def __init__(self, lm_base):
        super().__init__(lm_base)

    def login(self, username, password):
        url = '{0}/ui/api/login'.format(self.lm_base)
        data = {
            'username': username,
            'password': password
        }
        response = requests.post(url, json=data, verify=False)
        if response.status_code == 404 or response.status_code == 405:
            old_url = '{0}/api/login'.format(self.lm_base)
            logger.info('Failed to access login at {0} with {1} repsonse code...may be an older LM environment, trying {2}'.format(url, response.status_code, old_url))
            response = requests.post(old_url, json=data, verify=False)
        if response.status_code == 200:
            login_result = response.json()
            return login_result
        else:
            self._raise_unexpected_status_exception(response, error_prefx='Authentication request')

class LmSecurityCtrl:
    """
    Manages authentication with a target CP4NA orchestration environment 
    """

    def __init__(self, env):
        """
        Constructs a new instance of controller for a target CP4NA orchestration environment and target user

        Args:
            env (TNCOEnvironment): the target CP4NA orchestration environment for authentication
        """
        self.__env = env
        self.__auth_tracker = AuthTracker()
        # Using the new client authentication methods in the "legacy" driver so we only need to maintain one impl
        # Eventually this LmSecurityCtrl will be removed, once we switch all of the "lmctl project" functionality to use the new client

        self.__client = self.__env.build_client()

    def get_access_token(self):
        """
        Retrieves the current Access Token for the user. If there is no current Access Token then a request is made to authenticate the user and, if a valid attempt, a new Access Token is returned.
        If the Access Token has expired (or will within an unreasonable amount of time to make use of the Token) then a request is made to re-authenticate the user. 
        Any client making use of this Token should call this function for EACH request, rather than caching the Token, therefore making use of this functions handling of requesting new Tokens on behalf of the client.

        Returns:
            str: the current Access Token for the user
        """
        if self.__need_new_token():
            logger.debug('Requesting new access token')
            auth_response = self.__client.auth_type.handle(self.__client)
            self.__auth_tracker.accept_auth_response(auth_response)
        return self.__auth_tracker.current_access_token

    def __need_new_token(self):
        """
        Determines if we need an Access Token by checking if there is one already, if there is then check it hasn't expired (using local knowledge of when the token would expire).
        This method adds a "wait period" of 1 second to any previous Access Token expiration time, meaning if the Token is going to expire within 
        1 second it waits till the Token expires before returning True to indicate a new one is needed. This gives clients a reasonable time to use the Token after checking it.

        Returns:
            bool: True if there is no Access Token for the user or it is believed to be expired based on time of last authentication
        """
        return self.__auth_tracker.has_access_expired

    def add_access_headers(self, headers=None):
        """
        Helper method to get the current Access Token and add it to the specified headers

        Returns:
          obj: the headers object passed in (or a new dictionary is created), with the addition of the 'Authorization' key populated with the current Access Token
        """
        if headers is None:
            headers = {}
        access_token = self.get_access_token()
        headers['Authorization'] = 'Bearer {0}'.format(access_token)
        return headers
