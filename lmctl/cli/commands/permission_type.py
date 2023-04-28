import click
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from .actions import get, retry, rollback, cancel
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import List
from lmctl.cli.io import IOController

__all__ = (
    'get_permission_types',
)

from ..arguments import set_param_option

tnco_builder = TNCOCommandBuilder(
    singular='permissiontype',
    plural='permissiontypes',
    display_name='Permission Type'
)

id_arg = Identifier(param_name='id')

default_columns = [
    Column('name', header='Name'),
    Column('description', header='Description'),
]

@tnco_builder.make_get_command(
    identifiers=[id_arg],
    identifier_required=False,
    default_columns=default_columns,
    allow_file_input=False
)
@click.argument(id_arg.param_name, required=False)
def get_permission_types(
        tnco_client: TNCOClient,
        identity: Identity,
    ):
    api = tnco_client.permission_types
    if identity is not None:
        return api.get(identity.value)
    return api.query()
