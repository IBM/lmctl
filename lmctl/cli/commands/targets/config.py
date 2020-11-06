import click
from .target import Target
from lmctl.config import ConfigFinder, get_config, ConfigError
from lmctl.cli.safety_net import safety_net
from lmctl.cli.format import YamlFormat
from lmctl.cli.io import IOController
import os

config_template = '''\
environments:
  default:
    tnco:
      ### General 
      
      # The full HTTP(s) address used to access the API gateway of your TNCO instance
      address: https://example.com

      # Set to true if TNCO is secure and requires authentication to use the APIs
      secure: True

      ### Authentication
      ### Required if "secure" is true.

      # Auth Option 1: TNCO Client credentials
      # ID of the client credentials to authenticate with
      client_id: LmClient
      # Secret for the above client
      client_secret: enter-your-secret

      # Auth Option 2: TNCO User based access
      # ID of the client credentials with password scope authentication enabled
      #client_id: LmClient
      # Secret for the above client
      #client_secret: enter-your-secret
      # The username to authenticate with
      #username: jack
      # The password for the above user
      #password: enter-your-pass
      
      # Auth Option 3: TNCO "unofficial" user based access. 
      # Using username/password without client credentials is not supported by TNCO so could stop functioning in any future release
      # The username to authenticate with
      #username: jack
      # The password for the above user
      #password: enter-your-pass
'''

class Configuration(Target):
    name = 'config'
    plural = 'configs'
    display_name = 'Configuration'

    def get(self):
        @click.command(help=f'Get the active LMCTL {self.display_name} file')
        @click.option('--print-path', is_flag=True, help='Print the path the configuration was loaded from')
        @click.option('--path-only', is_flag=True, help='Print only path')
        @click.pass_context
        def _get(ctx: click.Context, print_path: bool = False, path_only: bool = False):
            with safety_net(ConfigError):
                loaded_config, config_path = get_config()
            io = IOController.get()
            if path_only:
                io.print(config_path)
            else:
                with open(config_path, 'r') as f:
                    content = f.read()
                
                if print_path:
                    io.print(f'Path: {config_path}')
                    io.print('---')
                io.print(content)
        return _get

    def create(self):
        @click.command(help=f'Create starter LMCTL {self.display_name} file')
        @click.option('--path', help='Override the file path location the file is created in')
        @click.option('--overwrite', is_flag=True, help='Overwrite existing file at location (the existing file is renamed)')
        @click.pass_context
        def _create(ctx: click.Context, path: str = None, overwrite: bool = False):
            if path is None:
                path = ConfigFinder().get_default_config_path()
            if os.path.exists(path):
                if overwrite:
                    dir_path = os.path.dirname(path)
                    file_name = os.path.basename(path)
                    new_file_name = f'{file_name}.bak'
                    new_path = os.path.join(dir_path, new_file_name)
                    os.rename(path, new_path)
                    IOController.get().print(f'Moved existing file at "{path}" to "{new_path}"')
                else:
                    raise click.ClickException(f'Cannot create configuration file at path "{path}" because there is already a file there and "--overwrite" was not set')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(config_template)
            IOController.get().print(f'Created file: {path}')
        return _create

