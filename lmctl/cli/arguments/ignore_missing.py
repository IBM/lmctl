import click

def ignore_missing_option():
    def decorator(f):
        return click.option('--ignore-missing', 
                        help='Ignore if object not found',
                        is_flag=True
                        )(f)
    return decorator
