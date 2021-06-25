from .output_format import OutputFormat
from .input_format import InputFormat
from .exceptions import BadFormatError
from typing import List, Any, Dict
from lmctl.utils.dcutils.dc_to_dict import asdict
import dataclasses
import json 

class JsonFormat(OutputFormat, InputFormat):

    def convert_list(self, element_list: List[Any]) -> str:
        converted_element_list = []
        for e in element_list:
            if dataclasses.is_dataclass(type(e)):
                converted_element_list.append(asdict(e))
            else:
                converted_element_list.append(e)
        data = {'items': converted_element_list}
        try:
            return json.dumps(data, indent=2)
        except json.JSONDecodeError as e:
            raise BadFormatError(f'Failed to convert to JSON: {e}') from e

    def convert_element(self, element: Any) -> str:
        if dataclasses.is_dataclass(type(element)):
            element = asdict(element)
        try:
            return json.dumps(element, indent=2)
        except json.JSONDecodeError as e:
            raise BadFormatError(f'Failed to convert to JSON: {e}') from e

    def read(self, content: str) -> Dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise BadFormatError(f'Failed to read content as JSON: {e}') from e
