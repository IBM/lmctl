
class LmDriverException(Exception):
    pass

class LmDriverExceptionBuilder:

    def __init__(self):
        pass

    @staticmethod
    def error(response):
        raise LmDriverException('Request returned unexpected status code: {0}'.format(response.status_code))