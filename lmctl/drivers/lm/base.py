

class LmDriver:

    def __init__(self, lm_base, lm_security_ctrl=None):
        self.lm_base = lm_base
        self.lm_security_ctrl = lm_security_ctrl

    def _configure_access_headers(self, headers=None):
        if headers is None:
            headers = {}
        if self.lm_security_ctrl:
            return self.lm_security_ctrl.add_access_headers(headers)
        return headers

    def _raise_unexpected_status_exception(self, response):
        message = None
        try:
            json_body = response.json()
            if 'localizedMessage' in json_body:
                message = json_body['localizedMessage']
        except ValueError as e:
            pass
        error_msg = 'Request returned unexpected error: status_code={0}'.format(response.status_code)
        if message:
            error_msg += ', message={0}'.format(message)
        raise LmDriverException(error_msg)


class LmDriverException(Exception):
    pass


class NotFoundException(LmDriverException):
    pass
