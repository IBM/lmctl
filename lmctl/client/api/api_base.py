import requests 

class APIBase:

    def __init__(self, base_client: 'TNCOClient'):
        self.base_client = base_client
