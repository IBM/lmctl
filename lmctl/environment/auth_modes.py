
__all__ = (
    'ALL_AUTH_MODES',
    'NO_AUTH_MODE',
    'ZEN_AUTH_MODE',
    'CP_API_KEY_AUTH_MODE',
    'TOKEN_AUTH_MODE',
    'OAUTH_MODE',
    'OAUTH_USER_MODE',
    'OAUTH_LEGACY_USER_MODE',
    'OAUTH_CLIENT_MODE',
    'OKTA_MODE',
    'OKTA_USER_MODE',
    'OKTA_CLIENT_MODE',
    'is_no_auth_mode',
    'is_okta_mode',
    'is_okta_user_mode',
    'is_okta_client_mode',
    'is_oauth_mode',
    'is_oauth_user_mode',
    'is_oauth_client_mode',
    'is_oauth_legacy_user_mode',
    'is_cp_api_key_mode',
    'is_token_mode',
)

NO_AUTH_MODE = 'none'

ZEN_AUTH_MODE = 'zen' #Deprecated - use CP_API_KEY_AUTH_MODE
CP_API_KEY_AUTH_MODE = 'cp-api-key'

TOKEN_AUTH_MODE = 'token'

OAUTH_MODE = 'oauth' #Deprecated - use OAUTH_USER_MODE, OAUTH_LEGACY_USER_MODE, OAUTH_CLIENT_MODE
OAUTH_USER_MODE = 'user'
OAUTH_LEGACY_USER_MODE = 'user-login'
OAUTH_CLIENT_MODE = 'client-credentials'

OKTA_MODE = 'okta' #Deprecated - use OKTA_USER_MODE or OKTA_CLIENT_MODE
OKTA_USER_MODE = 'okta-user'
OKTA_CLIENT_MODE = 'okta-client'

ALL_AUTH_MODES = [NO_AUTH_MODE, CP_API_KEY_AUTH_MODE, TOKEN_AUTH_MODE, OAUTH_USER_MODE, OAUTH_CLIENT_MODE, OAUTH_LEGACY_USER_MODE, OKTA_CLIENT_MODE, OKTA_USER_MODE]

def is_no_auth_mode(mode: str):
    return mode == None or _check_if_mode(mode, NO_AUTH_MODE)

def is_okta_mode(mode: str):
    return _check_if_mode(mode, OKTA_MODE)

def is_okta_user_mode(mode: str):
    return _check_if_mode(mode, OKTA_USER_MODE)

def is_okta_client_mode(mode: str):
    return _check_if_mode(mode, OKTA_CLIENT_MODE)

def is_oauth_mode(mode: str):
    return _check_if_mode(mode, OAUTH_MODE) 

def is_oauth_user_mode(mode: str):
    return _check_if_mode(mode, OAUTH_USER_MODE)

def is_oauth_client_mode(mode: str):
    return _check_if_mode(mode, OAUTH_CLIENT_MODE)

def is_oauth_legacy_user_mode(mode: str):
    return _check_if_mode(mode, OAUTH_LEGACY_USER_MODE)

def is_cp_api_key_mode(mode: str):
    return _check_if_mode(mode, CP_API_KEY_AUTH_MODE) or _check_if_mode(mode, ZEN_AUTH_MODE)

def is_token_mode(mode: str):
    return _check_if_mode(mode, TOKEN_AUTH_MODE)

def _check_if_mode(input_mode: str, target_mode: str):
    if type(input_mode) == str:
        input_mode = input_mode.lower()
    if type(target_mode) == str:
        target_mode = target_mode.lower()
    
    return input_mode == target_mode

