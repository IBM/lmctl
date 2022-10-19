import os
import click
from .actions import get, create
from .utils import pass_io
from lmctl.cli.io import IOController
from lmctl.cli.tags import SETTINGS_TAG
from lmctl.config import get_config_with_path, find_config_location
from lmctl.cli.arguments import overwrite_file_option, output_file_option

__all__ = (
    'get_config',
    'create_config'
)

singular = 'config'
plural = 'configs'
display_name = 'Configuration'

@get.command(singular, aliases=[plural], tags=[SETTINGS_TAG], help=f'Get the active LMCTL {display_name} file')
@click.option('--print-path', is_flag=True, default=False, show_default=True, help='Print the path the configuration was loaded from')
@click.option('--path-only', is_flag=True, default=False, show_default=True, help='Print only path')
@pass_io
def get_config(print_path: bool, path_only: bool, io: IOController):
    loaded_config, config_path = get_config_with_path()
    if path_only:
        io.print(config_path)
    else:
        with open(config_path, 'r') as f:
            content = f.read()
        if print_path:
            io.print(f'Path: {config_path}')
            io.print('---')
        io.print(content)

@create.command(singular, aliases=[plural], tags=[SETTINGS_TAG], help=f'Create starter LMCTL {display_name} file')
@output_file_option(help='Set the file path location the file is created in')
@overwrite_file_option(help='Overwrite existing file at location (the existing file is renamed)')
def create_config(path: str = None, overwrite: bool = False):
    io = IOController.get()
    if path is None:
        path = find_config_location()
    if os.path.exists(path):
        if overwrite:
            dir_path = os.path.dirname(path)
            file_name = os.path.basename(path)
            new_file_name = f'{file_name}.bak'
            new_path = os.path.join(dir_path, new_file_name)
            os.rename(path, new_path)
            io.print(f'Moved existing file at "{path}" to "{new_path}"')
        else:
            raise click.UsageError(f'Cannot create configuration file at path "{path}" because there is already a file there and "--overwrite" was not set')
    dir_path = os.path.dirname(path)
    if dir_path is not None and len(dir_path) > 0:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(config_template)
    io.print(f'Created file: {path}')

config_template = '''\
environments:
  default:
    tnco:
      ###############
      #  General    #
      ###############
      
      ## The full HTTP(s) address used to access the API gateway (Ishtar route) of your TNCO instance
      address: https://ishtar-route.ocp.example.com

      ## Set to true if TNCO is secure and requires authentication to use the APIs
      secure: True

      #####################################################################
      #  Zen Authentication                                               #
      #  Required if "secure" is true and not using Oauth or Token        #
      #####################################################################
      
      # Indicate environment is using Zen
      #auth_mode: zen

      ## The full HTTP(s) address and path used to access the Zen authentication APIs E.g. https://<hostname>/icp4d-api/v1/authorize
      #auth_address: https://zen-route.ocp.example.com/icp4d-api/v1/authorize

      ## The username to authenticate with
      #username: example-user

      ## The API key for the above user
      #api_key: enter-your-api-key

      #####################################################
      # Oauth Authentication                              #
      #####################################################
     
      # Indicate the environment is using oauth
      auth_mode: oauth 

      #=========================#
      # Oauth Option 1:         #
      # TNCO Client credentials #
      #=========================#

      ## ID of the client credentials to authenticate with
      client_id: LmClient
      
      ## Secret for the above client
      #client_secret: enter-your-secret

      #=========================#
      # Oauth Option 2:         #
      # TNCO User based access  #
      #=========================#

      ## ID of the client credentials with password scope authentication enabled
      #client_id: LmClient

      ## Secret for the above client
      #client_secret: enter-your-secret

      ## The username to authenticate with
      #username: jack

      ## The password for the above user
      #password: enter-your-pass
      
      #=================================#
      # Oauth Option 3:                 #
      # "unofficial" user based access  #
      #=================================#

      ## Using username/password without client credentials is not supported by TNCO so could stop functioning in any future release
      ## The username to authenticate with
      #username: jack
      
      ## The password for the above user
      #password: enter-your-pass

      #####################################################
      # Token Authentication                              #
      #####################################################
     
      # Indicate the environment is using token based auth
      auth_mode: token 

      #token: enter-your-token
'''