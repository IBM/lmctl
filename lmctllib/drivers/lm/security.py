import datetime
import requests
import logging
import time
from .exception import LmDriverExceptionBuilder

logger = logging.getLogger(__name__)

class LmSecurityDriver:
    """
    Client for LM Security APIs
    """
    def __init__(self, lm_base):
        """
        Constructs a new instance of the driver

        Args:
            lm_base (str): the base URL of the target LM environment e.g. http://ui.lm:32080
        """
        self.lm_base=lm_base

    def login(self, username, password):
        url = '{0}/api/login'.format(self.lm_base)
        data =  {
            'username': username,
            'password': password
        }
        response = requests.post(url, json=data, verify=False)
        if response.status_code == 200:
            login_result = response.json()
            return login_result
        else:
            LmDriverExceptionBuilder.error(response)

class LmSecurityCtrl:
    """
    Manages authentication with a target LM environment 
    """
    def __init__(self, login_address, username, password):
        """
        Constructs a new instance of controller for a target LM environment and target user

        Args:
            login_address (str): the base URL of the target LM environment for authentication e.g. http://ui.lm:32080
            username (str): the username to authenticate as
            password (str): the password for the specified username
        """
        self.__driver = LmSecurityDriver(login_address)
        self.__username = username
        self.__password = password
        self.__login_result = None
        self.__login_time = None

    def getAccessToken(self):
        """
        Retrieves the current Access Token for the user. If there is no current Access Token then a request is made to authenticate the user and, if a valid attempt, a new Access Token is returned.
        If the Access Token has expired (or will within an unreasonable amount of time to make use of the Token) then a request is made to re-authenticate the user. 
        Any client making use of this Token should call this function for EACH request, rather than caching the Token, therefore making use of this functions handling of requesting new Tokens on behalf of the client.
        
        Returns:
            str: the current Access Token for the user
        """
        if self.__needNewToken():
            logger.debug('Requesting new access token')
            self.__login_result = self.__driver.login(self.__username, self.__password)
            self.__login_time = datetime.datetime.now()
        return self.__login_result['accessToken']

    def __needNewToken(self):
        """
        Determines if we need an Access Token by checking if there is one already, if there is then check it hasn't expired (using local knowledge of when the token would expire).
        This method adds a "wait period" of 1 second to any previous Access Token expiration time, meaning if the Token is going to expire within 
        1 second it waits till the Token expires before returning True to indicate a new one is needed. This gives clients a reasonable time to use the Token after checking it.
        
        Returns:
            bool: True if there is no Access Token for the user or it is believed to be expired based on time of last authentication
        """
        if not self.__login_result:
            logger.debug('No current access token, must request one')
            return True
        else:
            logger.debug('Checking if access token has expired')
            expiration_seconds = self.__login_result['expiresIn']
            now = datetime.datetime.now()
            logged_in_time = (now - self.__login_time).total_seconds()
            logger.debug('Logged in for {0} seconds, token had an expiration time of {1} seconds'.format(logged_in_time, expiration_seconds))
            if logged_in_time >= expiration_seconds:
                logger.debug('Token expired, must request a new one')
                return True
            # If the token expires within 1 second, wait and get a new one
            if logged_in_time >= (expiration_seconds-1):
                logger.debug('Expires in less than 1 second, waiting before requesting a new Token')
                time.sleep(2)
                return True
        return False

    def addAccessHeaders(self, headers=None):
        """
        Helper method to get the current Access Token and add it to the specified headers

        Returns:
          obj: the headers object passed in (or a new dictionary is created), with the addition of the 'Authorization' key populated with the current Access Token
        """
        if headers is None:
            headers = {}
        access_token = self.getAccessToken()
        headers['Authorization'] = 'Bearer {0}'.format(access_token)
        return headers
