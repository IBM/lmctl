import click

global_io = None

class IOController:

    @staticmethod
    def get():
        global global_io
        if global_io is None:
            global_io = IOController()
        return global_io
    
    def prompt(self, *args, **kwargs):
        click.prompt(*args, **kwargs)

    def print_error(self, text):
        self.__print(text, err=True)

    def print(self, text):
        self.__print(text)

    def __print(self, text, **kwargs):
        click.echo(text, **kwargs)
