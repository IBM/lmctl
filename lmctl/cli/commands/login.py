import click
import os
import logging
from pydantic import ValidationError
from lmctl.config import find_config_location, write_config
from lmctl.environment import (TNCOEnvironment, EnvironmentGroup, TOKEN_AUTH_MODE, CP_API_KEY_AUTH_MODE,
                               OAUTH_MODE,  OKTA_MODE)
from lmctl.cli.controller import get_global_controller, CLIController
from lmctl.cli.commands.utils import mutually_exclusive_group

logger = logging.getLogger(__name__)
@click.command(short_help='Authenticate and optionally save credentials')
@click.pass_context
@click.argument('address')
@click.option('-u', '--username', default=None, help=f'Username')
@click.option('-p', '--pwd', '--password', default=None, help=f'Password for the given user. Omit this option to be prompted for the value instead')
@click.option('--api-key', default=None, help=f'API Key for the given user')
@click.option('--client', 'client_id', default=None, help=f'Client ID')
@click.option('--client-secret', default=None, help=f'Secret for the given Client ID')
@click.option('--scope', default=None, help=f'Scope for the given Client ID')
@click.option('--auth-server-id', default=None, help=f'Okta backend authentication server for the given Client ID to generate okta auth API')
@click.option('--token', default=None, help=f'Authenticate with a token instead of credentials')
@click.option('--auth-address', default=None, help=f'Alternative address used for authentication request for some user based login flows')
@click.option('--name', default='default', show_default=True, help='Name given to the environment saved in the configuration file')
@click.option('--save-creds', is_flag=True, default=False, show_default=True, help='Not recommended - but an option to save the credentials instead of the token. This allows lmctl to re-authenticate later without requiring a login. Your credentials will be stored as plain text in the configuration file!')
@click.option('--print', 'print_token', is_flag=True, default=False, help='Print the access token rather than saving it')
@click.option('-y', 'yes_to_prompts', is_flag=True, default=False, show_default=True, help='Force command to accept all confirmation prompts e.g. to override existing environment with the same name')
@click.option('--zen', 'is_zen', is_flag=True, default=False, help=f'Indicates Cloud Pak API key to be provided')
@click.option('--okta', 'is_okta', is_flag=True, default=False, help=f'Indiciates Okta user to be provided')
@mutually_exclusive_group(
    ('token', '--token'),
    mutex_with=[
        ('username', '--username'),
        ('password', '-p, --pwd, --password'),
        ('client_id', '--client-id'),
        ('client_secret', '--client-secret'),
        ('auth_address', '--auth-address'),
        ('auth-server-id', '--auth_server_id'),
        ('scope', '--scope'),
        ('api-key', '--api-key'),
        ('is_zen', '--zen'),
        ('is_okta', '--okta'),
    ]
)
def login(ctx: click.Context, address: str, auth_mode: str = None, username: str = None, pwd: str = None, api_key: str = None, client_id: str = None, client_secret: str = None, scope: str = None, auth_server_id: str = None,
            token: str = None, name: str = None, auth_address: str = None, save_creds: bool = False, yes_to_prompts: bool = False, print_token: bool = False, is_zen: bool = False, is_okta: bool = False):
    """
    Authenticates with an environment and save the access token in your lmctl config file for subsequent use. 
    
    A single use token is obtained using the credentials and this token is persisted in the lmctl config file, instead of your credentials. 
    Once the token has expired, you will no longer be able to access this environment and will need to call "login" again.
    
    To avoid leaking your credentials in your command history it is recommended that you exclude "--client-secret", "--password" and "--api-key" from your command. 
    You will be prompted for these where appropriate.
    
    Using "--save-creds" will persist the credentials in the lmctl config file instead, which will allow lmctl to reauthenticate on your behalf when the current access token expires. 
    This is discouraged as the config file is plain text and easily accessed on your environment.
    
    You can check the contents of your local lmctl config file at any time with "lmctl get config"
    """
    
    # Support missing config file by pre-creating one
    path = find_config_location(ignore_not_found=True)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('environments: {}')

    ctl = get_global_controller(override_config_path=path)

    _print_warnings(ctl, path, save_creds, pwd, api_key, client_secret)

    if token is None and client_id is None and username is None:
        # No credentials passed, must prompt
        if is_zen:
            auth_address = _prompt_if_not_set(ctl, 'Cloud Pak Front Door Address (cpd)', auth_address)
            username = _prompt_if_not_set(ctl, 'Username', username)
            api_key = _prompt_if_not_set(ctl, 'API Key', api_key, secret=True)
        else:
            # If auth address is not set then we must prompt for client credentials in addition to username/password
            if auth_address is None:
                client_id = _prompt_if_not_set(ctl, 'Client ID', client_id)
                client_secret = _prompt_if_not_set(ctl, 'Client Secret', client_secret, secret=True)
            username = _prompt_if_not_set(ctl, 'Username', username)
            pwd = _prompt_if_not_set(ctl, 'Password', pwd, secret=True)
    elif token is None:
        if client_id is not None:
            client_secret = _prompt_if_not_set(ctl, 'Client Secret', client_secret, secret=True)
        if username is not None:
            if client_id is None and auth_address is None:
                raise click.BadArgumentUsage(message=f'Must specify "--auth-address" option when attempting to authenticate with username/password/api_key but without client/client-secret', ctx=ctx)
            if is_zen:
                api_key = _prompt_if_not_set(ctl, 'API Key', api_key, secret=True)
            else:
                pwd = _prompt_if_not_set(ctl, 'Password', pwd, secret=True)

    auth_mode = OAUTH_MODE
    cp_front_door_address = None
    
    if token is not None:
        auth_mode = TOKEN_AUTH_MODE
    elif is_zen:
        auth_mode = CP_API_KEY_AUTH_MODE
        cp_front_door_address = auth_address
        auth_address = None # cp_front_door_address set instead
    elif is_okta:
        auth_mode = OKTA_MODE

    try:
        tnco_env = TNCOEnvironment(
            address=address,
            secure=True,
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            auth_server_id=auth_server_id,
            username=username,
            password=pwd,
            api_key=api_key,
            token=token,
            auth_mode=auth_mode,
            auth_address=auth_address,
            cp_front_door_address=cp_front_door_address
        )
    except ValidationError as e:
        logger.exception('Error creating TNCOEnvironment')
        user_friendly_errors = []
        for error in e.errors():
            user_friendly_errors.append(error['msg'])
        user_friendly_errors_str = ', '.join(user_friendly_errors)
        ctl.io.print_error(f'Error: {user_friendly_errors_str}')
        exit(1)
    client = tnco_env.build_client()
    access_token = client.get_access_token()

    if print_token:
        ctl.io.print(access_token)
    else:
        ctl.io.print('Login success')
        name = _ensure_name(ctl, name, yes_to_prompts)

        if not save_creds or token is not None:
            tnco_env_dict = {
                'address': address,
                'token': access_token,
                'auth_mode': TOKEN_AUTH_MODE
            }
        else:
            tnco_env_dict = {
                'address': address,
                'auth_mode': auth_mode
            }
            if client_id is not None:
                tnco_env_dict['client_id'] = client_id
            if client_secret is not None:
                tnco_env_dict['client_secret'] = client_secret
            if username is not None:
                tnco_env_dict['username'] = username
            if pwd is not None:
                tnco_env_dict['password'] = pwd
            if auth_address is not None:
                tnco_env_dict['auth_address'] = auth_address
            if api_key is not None:
                tnco_env_dict['api_key'] = api_key
            if scope is not None:
                tnco_env_dict['scope'] = scope
            if auth_server_id is not None:
                tnco_env_dict['auth_server_id'] = auth_server_id
            if cp_front_door_address is not None:
                tnco_env_dict['cp_front_door_address'] = cp_front_door_address
        tnco_env = TNCOEnvironment(**tnco_env_dict)

        # Write
        if name not in ctl.config.environments:
            ctl.config.environments[name] = EnvironmentGroup(name=name)
        ctl.config.environments[name].tnco = tnco_env
        ctl.config.active_environment = name
        ctl.io.print(f'Updating config at: {ctl.config_path}')
        write_config(ctl.config, override_config_path=ctl.config_path)

def _ensure_name(ctl: CLIController, name: str = None, yes_to_prompts: bool = False) -> str:
    if name is None:
        name = 'default'
    if name in ctl.config.environments:
        if not yes_to_prompts:
            ctl.io.confirm_prompt(f'An environment with name "{name}" already exists, do you want to override it?', abort=True)
    return name

def _prompt_if_not_set(ctl: CLIController, name: str, value: str = None, secret: bool = False) -> str:
    if value is None:
        value = ctl.io.prompt(name, hide_input=secret, default='')
    return value

def _print_warnings(ctl: CLIController, path, save_creds, password, api_key, client_secret):
    
    if save_creds:
        ctl.io.print_warning(f'WARNING: using "--save-creds" is not recommended as credentials will be stored in plain text file {path}')

    if password:
        ctl.io.print_warning(f'WARNING: specfiying the "--password" option may leak the value to your terminal history '\
                             'and should be used with caution. Omit this option and you will be prompted to safely enter the value instead')

    if api_key:
        ctl.io.print_warning(f'WARNING: specfiying the "--api-key" option may leak the value to your terminal history '\
                             'and should be used with caution. Omit this option and you will be prompted to safely enter the value instead')
         
    if client_secret:
        ctl.io.print_warning(f'WARNING: specfiying the "--client-secret" option may leak the value to your terminal history '\
                             'and should be used with caution. Omit this option and you will be prompted to safely enter the value instead')
