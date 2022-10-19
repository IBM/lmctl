import click
import os
from lmctl.cli.controller import get_global_controller
from lmctl.cli.arguments import OutputFormatOption, OutputFileOption, OverwriteOption
from lmctl.cli.format import YamlFormat, JsonFormat, OutputFormat

__all__ = (
    'TNCOGenerateCommand',
)

class TNCOGenerateCommand(click.Command):
    
    def __init__(self, 
                type_display_name: str, 
                *args, 
                additional_help: str = None, 
                **kwargs
            ):
        self.type_display_name = type_display_name
        self.additional_help = additional_help
        if 'help' not in kwargs or kwargs['help'] is None:
            kwargs['help'] = self._build_help()
        if 'short_help' not in kwargs or kwargs['short_help'] is None:
            kwargs['short_help'] = f'Generate an example file for a {self.type_display_name}'
        super().__init__(*args, **kwargs)
        self.params.append(OutputFormatOption())
        self.params.append(OutputFileOption())
        self.params.append(OverwriteOption())

        self.generate_behaviour = self.callback
        self.callback = self._callback

    def _callback(self, 
                    *args, 
                    output_format: OutputFormat,
                    path: str,
                    overwrite: bool,
                    **kwargs):

        result = self.generate_behaviour(*args, **kwargs)

        io = get_global_controller().io
        if isinstance(result, list):
            formatted_result = output_format.convert_list(result)
        else:
            formatted_result = output_format.convert_element(result)
        
        # Write file
        if path is None:
            path = ''.join(c for c in self.type_display_name.lower() if c.isalnum())
            if isinstance(output_format, YamlFormat):
                path += '.yaml'
            elif isinstance(output_format, JsonFormat):
                path += '.json'

        if os.path.exists(path) and not overwrite:
            raise ValueError(f'File with name "{path}" already exists. Choose different file path or use "--overwrite" to replace the existing file')
        
        with open(path, 'w') as f:
            f.write(formatted_result)

        io.print(f'Generated file: {path}')


    def _build_help(self) -> str:
        return f'Generate an example file for a {self.type_display_name}'
     