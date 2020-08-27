import json
import yaml

class LmClientError(Exception):
    pass

class LmClientHttpError(LmClientError):
    
    def __init__(self, msg, cause, *args, **kwargs):
        self.msg = msg
        self.cause = cause
        self._read_cause()
        full_msg = f'{msg}: status={self.status_code}, details={self.detail_message}'
        super().__init__(full_msg, *args, **kwargs)

    def _read_cause(self):
        self.status_code = self.cause.response.status_code
        self.headers = self.cause.response.headers
        self.body = None
        if self.headers.get('Content-Type', None) == 'application/json':
            try:
                self.body = self.cause.response.json()
            except ValueError as e:
                pass
        elif self.headers.get('Content-Type', None) == 'application/yaml':
            try:
                self.body = yaml.safe_load(self.cause.response.text)
            except yaml.YAMLError as e:
                pass
        if self.body is not None and isinstance(self.body, dict):
            if 'localizedMessage' in self.body:
                self.detail_message = self.body.get('localizedMessage')
            elif 'message' in self.body:
                self.detail_message = self.body.get('message')
        else:
            self.detail_message = str(self.cause)