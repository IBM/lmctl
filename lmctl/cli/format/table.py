from .output_format import OutputFormat
from typing import Union, Callable, List, Any
from tabulate import tabulate

class Column:

    def __init__(self, name: str, header: str = None, accessor: Union[str, callable] = None):
        self.name = name
        self.header = header
        self.accessor = accessor

class Table:
    columns: List[Column] = []

class TableFormat(OutputFormat):

    def __init__(self, headers: List[str] = None, row_processor: Callable = None, table: Table = None):
        if table is not None:
            if headers is not None or row_processor is not None:
                raise ValueError('"headers" and "row_processor" should NOT be supplied when "table" is set')
            self.table = table
            self.headers = None
            self.row_processor = None
        else:
            self.table = None
            if headers is None or row_processor is None:
                raise ValueError('"headers" and "row_processor" must be supplied when "table" is None')
            self.headers = headers
            self.row_processor = row_processor

    def _get_columns(self):
        if self.table is None:
            return None
        columns_access = self.table.columns
        if callable(columns_access):
            columns = columns_access()
        else:
            columns = columns_access
        try:
            iterator = iter(columns)
        except TypeError as e:
            raise TypeError(f'Could not iterate columns on table "{self.table}"') from e
        else:
            for c in columns:
                if not isinstance(c, Column):
                    raise TypeError(f'Found an instance of "{type(c)}" in table "{self.table}" columns when they must be an instance of "{Column.__name__}"')
        return columns

    def convert_list(self, element_list: List[Any]):
        columns = self._get_columns()
        if columns is None:
            headers = self.headers
        else:
            headers = []
            for c in columns:
                if c.header is not None:
                    headers.append(c.header)
                else:
                    headers.append(c.name)
        rows = []
        for element in element_list:
            rows.append(self.__element_to_table_row(element, columns))
        return tabulate(rows, headers=headers, tablefmt='orgtbl')

    def convert_element(self, element: Any):
        return self.convert_list([element])

    def __element_to_table_row(self, element: Any, columns: List[Column]):
        row = []
        if columns is None:
            row = self.row_processor(element)
            if row is None:
                row = []
        else:
            for c in columns:
                if c.accessor is None:
                    if isinstance(element, dict):
                        value = element.get(c.name)
                    else:
                        value = getattr(element, c.name, None)
                elif callable(c.accessor):
                    value = c.accessor(element)
                else:
                    if isinstance(element, dict):
                        value = element.get(c.accessor)
                    else:
                        value = getattr(element, c.accessor, None)
                row.append(value)
        return row
