from typing import List

class DictStore:

    def __init__(self, primary_key: str, unique_index_keys: List[str]=None, search_index_keys: List[str]=None):
        self.data = {}
        self.primary_key = primary_key
        self.unique_indexes = {}
        if unique_index_keys is not None:
            for key in unique_index_keys:
                self.unique_indexes[key] = {}
        self.search_indexes = {}
        if search_indexes_keys is not None:
            for key in search_index_keys:
                self.search_indexes[key] = {}

    def _ensure_pk(self, obj):
        if self.primary_key not in obj:
            raise ValueError('Obj missing primary key: {primary_key_attr}')

    def _ensure_unique(self, obj):
        pk = obj.get(self.primary_key)
        if pk in self.data:
            raise ValueError(f'Obj with pk "{self.primary_key}" value "{pk}" already exists')
        for index_key in self.

    def add(self, obj):
        self._ensure_pk(obj)
        for idx_attr in self.unique_index_attrs:
            