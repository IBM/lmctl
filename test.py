

import click

@click.group()
def cli():
    pass

@click.command()
@click.pass_context
@click.argument('address')
@click.option('--api-key', default=None)
def login(ctx, address = None, api_key = None):
    print("login!")
    print(address)
    print(api_key)
 
cli.add_command(login)

if __name__ == '__main__':
    cli()