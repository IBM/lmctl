import click
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from .actions import get, retry, rollback, cancel
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import List
from lmctl.cli.io import IOController

__all__ = (
    'get_objectgroup',
)

from ..arguments import set_param_option

tnco_builder = TNCOCommandBuilder(
    singular='objectgroup',
    plural='objectgroups',
    display_name='Objectgroups'
)

id_arg = Identifier(param_name='id')

default_columns = [
    Column('id', header='ID'),
    Column('name', header='Name'),
    Column('description', header='Description'),
    Column('isDefault', header='Is Default'),
    # Column('objectgroup', header='Object Group', accessor=lambda x: x.get('name') + ' (' + x.get('id') + ')'),
]

@tnco_builder.make_get_command(
    identifiers=[id_arg],
    identifier_required=False,
    default_columns=default_columns,
    allow_file_input=False
)
@click.argument(id_arg.param_name, required=False)
@click.option('--permission', help=f'Get the list of object groups to those the user has permission on.')
def get_objectgroup(
        tnco_client: TNCOClient,
        identity: Identity,
        permission: str,
    ):
    api = tnco_client.object_groups
    if identity is not None:
        return api.get(identity.value)
    elif permission is not None:
        query_param ={ "permission" : permission}
        return api.query(**query_param)
    return api.query()
