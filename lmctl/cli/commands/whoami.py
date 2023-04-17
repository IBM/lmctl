import click
from lmctl.cli.controller import get_global_controller
from lmctl.cli.commands.utils import mutually_exclusive_group
from lmctl.client.constants import TOKEN_AUTH_MODE

@click.command(short_help='Show information about the active environment', help='Show information about the active environment')
@click.pass_context
@click.option('-t', '--show-token', is_flag=True, default=False, help='Print only the current user access token')
@click.option('-u', '--show-user', is_flag=True, default=False, help='Print only the user')
@click.option('-e', '--show-env', is_flag=True, default=False, help='Print only the environment details')
@mutually_exclusive_group(
    ('show_token', '-t, --show-token'),
    mutex_with=[
        ('show_user', '-u, --show-user'),
        ('show_env', '-e, --show-env'), 
    ]
)
@mutually_exclusive_group(
    ('show_user', '-u, --show-user'),
    mutex_with=[
        ('show_env', '-e, --show-env'), 
    ]
)
def whoami(ctx: click.Context, show_token: bool, show_user: bool, show_env: bool):
    ctl = get_global_controller()

    env = ctl.get_active_environment()
    if env is None:
        ctl.io.print_error(f'Error: active environment not configured. Run "lmctl use env <env-name>" to activate an environment')
        exit(1)
    tnco_env = env.tnco
    if tnco_env is None:
        ctl.io.print_error(f'Error: CP4NA orchestration environment not configured on group: {env.name}')
        exit(1)

    if show_token:
        token = tnco_env.build_client().get_access_token()
        if token is None:
            ctl.io.print(f'Error: No access token available')
            exit(1)
        ctl.io.print(token)
        exit(0)

    env_str = f'{env.name} ({tnco_env.address})'
    if show_env:
        ctl.io.print(env_str)
        exit(0)

    user_str = tnco_env.summarise_user()
    if show_user:
        ctl.io.print(user_str)
        exit(0)
    
    ctl.io.print(f'User: {user_str}')
    ctl.io.print(f'Environment: {env_str}')
