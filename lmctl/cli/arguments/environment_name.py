import click

def environment_name_option():
    def decorator(f):
        return click.option('-e', '--environment', 'environment_name', 
                        required=True,
                        help='Name of the environment from the configuration file to be used'
                        )(f)
    return decorator
