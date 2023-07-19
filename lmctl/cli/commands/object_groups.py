import click
from .utils import TNCOCommandBuilder, Identity, Identifier
from lmctl.client import TNCOClient
from lmctl.cli.format import Column

__all__ = (
    'get_object_group',
)

from ..arguments import set_param_option

tnco_builder = TNCOCommandBuilder(
    singular='objectgroup',
    plural='objectgroups',
    display_name='Object Groups'
)

id_arg = Identifier.arg_and_attr('id')

permission_type_opt = Identifier(
    param_name='permission',
    obj_attribute='permission',
    param_opts=['-p', '--permission']
)

default_group_opt = Identifier(
    param_name='default',
    param_opts=['-d', '--default']
)

default_columns = [
    Column('id', header='ID'),
    Column('name', header='Name'),
    Column('description', header='Description'),
    Column('isDefault', header='Default'),
]

@tnco_builder.make_get_command(
    identifiers=[id_arg, permission_type_opt, default_group_opt],
    identifier_required=False,
    default_columns=default_columns
)
@click.argument(id_arg.param_name, required=False)
@click.option(*permission_type_opt.param_opts, required=False, help='Retrieve all Object Group/Groups with the given permission (use "lmctl get permissiontypes" to view available options)')
@click.option(*default_group_opt.param_opts, is_flag=True, required=False, help='Retrieve the default Object Group')
def get_object_group(
        tnco_client: TNCOClient,
        identity: Identity
    ):
    api = tnco_client.object_groups
    if identity is not None:
        if identity.identifier.param_name == permission_type_opt.param_name:
            query_param ={ "permission" : identity.value}
            return api.query(**query_param)
        elif identity.identifier.param_name == id_arg.param_name:
            return api.get(identity.value)
        elif identity.identifier.param_name == default_group_opt.param_name:
            return api.get_default()
        
    return api.query()
