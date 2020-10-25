from .output_format import OutputFormat
from .input_format import InputFormat
from .exceptions import BadFormatError
from typing import List, Any, Dict
import json 

class JsonFormat(OutputFormat, InputFormat):

    def convert_list(self, element_list: List[Any]) -> str:
        data = {'items': element_list}
        return json.dumps(data, indent=2)

    def convert_element(self, element: Any) -> str:
        return json.dumps(element, indent=2)

    def read(self, content: str) -> Dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise BadFormatError(f'Failed to read content as JSON: {e}') from e
