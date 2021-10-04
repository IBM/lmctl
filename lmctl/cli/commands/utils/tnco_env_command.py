import click
from typing import Optional
from lmctl.cli.arguments import EnvironmentNameOption, TNCOClientSecretOption, TNCOPwdOption, TNCOTokenOption
from lmctl.cli.controller import get_global_controller
from lmctl.client import TNCOClient

class TNCOEnvironmentCommand(click.Command):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.append(EnvironmentNameOption())
        self.params.append(TNCOClientSecretOption())
        self.params.append(TNCOPwdOption())
        self.params.append(TNCOTokenOption())
        
    def _get_tnco_client(self, input_environment_name: Optional[str], input_pwd: Optional[str], input_client_secret: Optional[str], input_token: Optional[str]) -> TNCOClient:
        ctl = get_global_controller()
        tnco_client = ctl.get_tnco_client(input_environment_name, input_pwd=input_pwd, input_client_secret=input_client_secret, input_token=input_token)
        return tnco_client
