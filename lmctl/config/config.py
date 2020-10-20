
class Config:

    def __init__(self, environments=None):
        if environments is None:
            environments = {}
        self.environments = environments
