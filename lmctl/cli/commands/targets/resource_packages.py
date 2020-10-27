import click
from typing import Dict
from lmctl.client import LmClient, LmClientHttpError
from lmctl.cli.arguments import common_output_format_handler, ignore_missing_option
from lmctl.cli.format import Table, Column
from .lm_target import LmTarget, LmCmd

class ResourcePackages(LmTarget):
    name = 'resourcepkg'
    plural = 'resourcepkgs'
    display_name = 'Brent Resource Package'
    
    @LmCmd(short_help=f'Upload {display_name}', help=f'''Upload {display_name}\
                        \n\nNOTE: Resource Packages are not synonymous with LMCTL project packages, even when the project contains a Resource.
                        The package for an LMCTL package can be extracted to find the Resource Package with zip/tar, depending on the chosen package format for your project''')
    @click.option('-f',' --file', 'file_path', 
                    required=True,
                    type=click.Path(exists=True)
                )
    def create(self, lm_client: LmClient, ctx: click.Context, file_path: str):
        api = lm_client.resource_packages
        resource_name = api.create(file_path)
        return f'Created from package: {resource_name}'

    @LmCmd(short_help=f'Update {display_name}', help=f'''Update {display_name}\
                        \n\nNOTE: Resource Packages are not synonymous with LMCTL project packages, even when the project contains a Resource.
                        The package for an LMCTL package can be extracted to find the Resource Package with zip/tar, depending on the chosen package format for your project''')
    @click.argument('resource_name', required=True)
    @click.option('-f', '--file', 'file_path', 
                    required=True,
                    type=click.Path(exists=True)
                )
    def update(self, lm_client: LmClient, ctx: click.Context, resource_name: str, file_path: str):
        api = lm_client.resource_packages
        api.update(resource_name, file_path)
        return f'Updated package for: {resource_name}'

    @LmCmd()
    @click.argument('resource_name', required=True)
    @ignore_missing_option()
    def delete(self, lm_client: LmClient, ctx: click.Context, resource_name: str, ignore_missing: bool = None):
        api = lm_client.resource_packages
        try:
            result = api.delete(resource_name)
        except LmClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name {resource_name} (ignoring)')
                    return
            raise
        return f'Deleted package for: {resource_name}'