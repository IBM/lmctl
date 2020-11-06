import click

class Printer:

    def error(self, text):
        self.__print(text)

    def text(self, text):
        self.__print(text)

    def __print(self, text):
        click.echo(text)

printer = Printer()