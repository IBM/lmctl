import abc

class Mutator(abc.ABC):

    def apply(self, original_content):
        return original_content
