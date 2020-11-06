import json
import yaml

class TNCOClientError(Exception):
    pass

class TNCOClientHttpError(TNCOClientError):
    
    def __init__(self, msg, cause, *args, **kwargs):
        self.msg = msg
        self.cause = cause
        self._read_cause()
        full_msg = f'{msg}: status={self.status_code}, message={self.detail_message}'
        super().__init__(full_msg, *args, **kwargs)

    def _read_cause(self):
        self.status_code = self.cause.response.status_code
        self.headers = self.cause.response.headers
        self.body = self._parse_cause_response_body()
        if self.body is not None and isinstance(self.body, dict):
            if 'localizedMessage' in self.body:
                self.detail_message = self.body.get('localizedMessage')
            elif 'message' in self.body:
                self.detail_message = self.body.get('message')
            else:
                self.detail_message = str(self.body)
        else:
            self.detail_message = str(self.cause)

    def _parse_cause_response_body(self):
        body = None
        if self.headers.get('Content-Type', None) == 'application/json':
            try:
                body = self.cause.response.json()
            except ValueError as e:
                pass
        elif self.headers.get('Content-Type', None) == 'application/yaml':
            try:
                body = yaml.safe_load(self.cause.response.text)
            except yaml.YAMLError as e:
                pass
        return body