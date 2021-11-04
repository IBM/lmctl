import click
import os
from lmctl.client import TNCOClientBuilder, ClientCredentialsAuth, UserPassAuth, LegacyUserPassAuth, JwtTokenAuth, TOKEN_AUTH_MODE, OAUTH_MODE, ZEN_AUTH_MODE
from lmctl.config import ConfigFinder, find_config_location, write_config
from lmctl.environment import TNCOEnvironment, EnvironmentGroup
from lmctl.cli.controller import get_global_controller, CLIController
from lmctl.cli.cmd_tags import settings_tag

@settings_tag
@click.command(short_help='Authenticate and save credentials', help='Authenticate with an environment and save credentials in the lmctl config file for subsequent use')
@click.pass_context
@click.argument('address')
@click.option('-u', '--username', default=None, help='Username')
@click.option('-p', '--pwd', '--password', default=None, help='Password for the given user')
@click.option('--api-key', default=None, help='API Key for the given user (when using "--zen")')
@click.option('--client', 'client_id', default=None, help='Client ID')
@click.option('--client-secret', default=None, help='Secret for the given Client ID')
@click.option('--token', default=None, help='Authenticate with a token instead of credentials')
@click.option('--name', default='default', show_default=True, help='Name given to the environment saved in the configuration file')
@click.option('--auth-address', default=None, help='Auth address required for username/password access (without client credentials). This is usually the Nimrod route in your environment.')
@click.option('--save-creds', is_flag=True, default=False, show_default=True, help='Save the credentials instead of the token. This allows lmctl to re-authenticate later without requiring a login but your passwords will be stored as plain text in the configuration file')
@click.option('--print', 'print_token', is_flag=True, default=False, help='Print the access token rather than saving it')
@click.option('-y', 'yes_to_prompts', is_flag=True, default=False, show_default=True, help='Force command to accept all confirmation prompts e.g. to override existing environment with the same name')
@click.option('--zen', 'is_zen', is_flag=True, default=False, help='Indicate that the Zen authentication method should be used (must provide --api-key)')
def login(ctx: click.Context, address: str, username: str = None, pwd: str = None, api_key: str = None, client_id: str = None, client_secret: str = None, 
            token: str = None, name: str = None, auth_address: str = None, save_creds: bool = False, yes_to_prompts: bool = False, print_token: bool = False, is_zen: bool = False):
    
    # Support missing config file by pre-creating one
    path = find_config_location(ignore_not_found=True)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('environments: {}')

    ctl = get_global_controller(override_config_path=path)

    _error_if_set(ctx, '--token', token, '--username', username)
    _error_if_set(ctx, '--token', token, '-p, --pwd, --password', pwd)
    _error_if_set(ctx, '--token', token, '--client', client_id)
    _error_if_set(ctx, '--token', token, '--client-secret', client_secret)
    _error_if_set(ctx, '--token', token, '--auth-address', auth_address)
    _error_if_set(ctx, '--token', token, '--api-key', api_key)
    if is_zen:
        # Only test "is_zen" when set to True
        _error_if_set(ctx, '--token', token, '--zen', is_zen)


    if token is None and client_id is None and username is None:
        # No credentials passed, must prompt
        if is_zen:
            auth_address = _prompt_if_not_set(ctl, 'Auth Address', auth_address)
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
    if token is not None:
        auth_mode = TOKEN_AUTH_MODE
    elif is_zen:
        auth_mode = ZEN_AUTH_MODE

    tnco_env = TNCOEnvironment(
        address=address, 
        secure=True,
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=pwd,
        api_key=api_key,
        token=token,
        auth_mode=auth_mode,
        auth_address=auth_address
    )
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
                'secure': True,
                'token': access_token,
                'auth_mode': TOKEN_AUTH_MODE
            }
        else:
            tnco_env_dict = {
                'address': address,
                'secure': True,
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
        
def _error_if_set(ctx: click.Context, first_opt: str, first_opt_value: str, second_opt: str, second_opt_value: str):
    if first_opt_value is not None and second_opt_value is not None:
        raise click.BadArgumentUsage(message=f'Do not use "{first_opt}" option when using "{second_opt}" option', ctx=ctx)

def _prompt_if_not_set(ctl: CLIController, name: str, value: str = None, secret: bool = False) -> str:
    if value is None:
        value = ctl.io.prompt(name, hide_input=secret, default='')
    return value
