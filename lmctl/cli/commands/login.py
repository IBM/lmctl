import click
import os
from lmctl.client import TNCOClientBuilder, ClientCredentialsAuth, UserPassAuth, LegacyUserPassAuth, JwtTokenAuth, TOKEN_AUTH_MODE, LEGACY_OAUTH_MODE
from lmctl.config import ConfigParser, ConfigFinder
from lmctl.environment import TNCOEnvironment
from lmctl.cli.controller import get_global_controller, CLIController

@click.command(help='Authenticate with an environment and save credentials in the lmctl config file for subsequent use')
@click.pass_context
@click.argument('address')
@click.option('-u', '--username', default=None, help='Username')
@click.option('-p', '--pwd', '--password', default=None, help='Password for the given user')
@click.option('--client', 'client_id', default=None, help='Client ID')
@click.option('--client-secret', default=None, help='Secret for the given Client ID')
@click.option('--token', default=None, help='Authenticate with a token instead of credentials')
@click.option('--name', default='default', show_default=True, help='Name given to the environment saved in the configuration file')
@click.option('--auth-address', default=None, help='Auth address required for username/password access (without client credentials). This is usually the Nimrod route in your environment.')
@click.option('--save-creds', is_flag=True, default=False, show_default=True, help='Save the credentials instead of the token. This allows lmctl to re-authenticate later without requiring a login but your passwords will be stored as plain text in the configuration file')
@click.option('--print', 'print_token', is_flag=True, default=False, help='Print the access token rather than saving it')
@click.option('-y', 'yes_to_prompts', is_flag=True, default=False, show_default=True, help='Force command to accept all confirmation prompts e.g. to override existing environment with the same name')
def login(ctx: click.Context, address: str, username: str = None, pwd: str = None, client_id: str = None, client_secret: str = None, 
            token: str = None, name: str = None, auth_address: str = None, save_creds: bool = False, yes_to_prompts: bool = False, print_token: bool = False):
    
    # Support missing config file by pre-creating one
    path = ConfigFinder().get_default_config_path()
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write('environments: {}')

    ctl = get_global_controller()

    _error_if_set(ctx, '--token', token, '--username', username)
    _error_if_set(ctx, '--token', token, '-p, --pwd, --password', pwd)
    _error_if_set(ctx, '--token', token, '--client', client_id)
    _error_if_set(ctx, '--token', token, '--client-secret', client_secret)
    _error_if_set(ctx, '--token', token, '--auth-address', auth_address)

    if token is None and client_id is None and username is None:
        # No credentials passed, must prompt
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
                raise click.BadArgumentUsage(message=f'Must specify "--auth-address" option when attempting to authenticate with username/password but without client/client-secret', ctx=ctx)
            pwd = _prompt_if_not_set(ctl, 'Password', pwd, secret=True)

    tnco_env = TNCOEnvironment(
        name='login', 
        address=address, 
        secure=True,
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=pwd,
        token=token,
        auth_mode=TOKEN_AUTH_MODE if token is not None else LEGACY_OAUTH_MODE,
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
                'secure': True
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

        # Read as raw dict to prevent null/defaults being written
        parser = ConfigParser()
        config_dict = parser.from_file_as_dict(ctl.config_path)
        config_dict['active_environment'] = name
        if name not in config_dict['environments']:
            config_dict['environments'][name] = {}
        config_dict['environments'][name]['tnco'] = tnco_env_dict
        ctl.io.print(f'Updating config at: {ctl.config_path}')
        parser.write_config_from_dict(config_dict, ctl.config_path)

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
