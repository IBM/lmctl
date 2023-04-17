import jwt
import os

def decode_jwt(token, supported_algorithms=None):
    if supported_algorithms is None:
        env_algorithms = os.environ.get('LMCTL_JWT_ALGO', os.environ.get('LM_JWT_ALGO', None))
        if env_algorithms is None or len(env_algorithms.strip()) == 0:
            supported_algorithms = ['HS256', 'HS384', 'HS512']
        else:
            supported_algorithms = [env_algorithms]

    try:
        return jwt.decode(token, options={'verify_signature': False, 'verify_aud': False}, algorithms=supported_algorithms)
    except jwt.DecodeError as e:
        raise ValueError(f'Could not parse JWT token. Decoding error: {str(e)}') from e