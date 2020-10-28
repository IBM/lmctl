from .output_format import OutputFormat
from .input_format import InputFormat
from .exceptions import BadFormatError
from typing import List, Any, Dict
import yaml

class YamlFormat(OutputFormat):

    def convert_list(self, element_list: List[Any]) -> str:
        data = {'items': element_list}
        try:
            return yaml.dump(data, sort_keys=False)
        except yaml.YAMLError as e:
            raise BadFormatError(f'Failed to convert to YAML: {e}') from e

    def convert_element(self, element: Any) -> str:
        try:
            return yaml.dump(element, sort_keys=False)
        except yaml.YAMLError as e:
            raise BadFormatError(f'Failed to convert to YAML: {e}') from e

    def read(self, content: str) -> Dict:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise BadFormatError(f'Failed to read content as YAML: {e}') from e

