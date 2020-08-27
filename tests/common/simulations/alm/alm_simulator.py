from tinydb import TinyDB, Query, where
import shutil
import tempfile
import os

class DocStore:

    def __init__(self, tinydb: TinyDB, primary_key: str):
        self.tinydb = tinydb
        self.primary_key = primary_key
    
    def _ensure_pk(self, obj):
        if self.primary_key not in obj:
            raise ValueError(f'Obj missing primary key: {primary_key}')

    def _ensure_unique(self, obj):
        pk_value = obj.get(self.primary_key)
        existing = self.tinydb.search(where(self.primary_key) == pk_value)
        if len(existing) > 0:
            raise ValueError(f'Obj with pk "{self.primary_key}" value "{pk}" already exists')

    def _ensure_exists(self, obj):
        pk_value = obj.get(self.primary_key)
        existing = self.tinydb.search(where(self.primary_key) == pk_value)
        if len(existing) == 0:
            raise ValueError(f'Obj with pk "{self.primary_key}" value "{pk}" does not exist')

    def create(self, obj: dict):
        self._ensure_pk(obj)
        self._ensure_unique(obj)
        self.tinydb.insert(obj)
    
    def update(self, obj: dict):
        self._ensure_pk(obj)
        self._ensure_exists(obj)
        pk_value = obj.get(self.primary_key)
        self.tinydb.update(obj, where(self.primary_key) == pk_value)

    def delete(self, obj_pk_value: str):
        pass

class ALMSimulator:

    def __init__(self, db_dir: str=None):
        if db_dir is None:
            self.db_dir = tempfile.mkdtemp(prefix='alm_simulator')
            self.managed_db_dir = True
        else:
            self.db_dir = db_dir
            self.managed_db_dir = False
        self.dbs = {}
        self.db_files = []

    def destroy_data(self):
        if self.managed_db_dir:
            if os.path.exists(self.db_dir):
                shutil.rmtree(self.db_dir)
        else:
            for db_file in self.db_files:
                if os.path.exists(db_file):
                    os.remove(db_file)

    def _get_db_for_type(self, type_name: str) -> DocStore:
        if type_name not in self.dbs:
            db_file = os.path.join(self.db_dir, f'{type_name}.json')
            self.db_files.append(db_file)
            self.dbs[type_name] = DocStore(TinyDB(db_file, sort_keys=True, indent=4, separators=(',', ': ')))
        return self.dbs.get(type_name)

    def add(self, type_name: str, obj: dict):
        db = self._get_db_for_type(type_name)