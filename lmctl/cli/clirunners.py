import click
import lmctl.drivers.lm.base as lm_drivers
import traceback
import logging

logger = logging.getLogger(__name__)

class ExceptionSafetyNet:

    def __enter__(self):
        pass

    def safety_net(self, etype, value, traceback):
        if value and isinstance(value, Exception):
            logger.exception(value)
            click.echo('Error: {0}'.format(str(value)), err=True)
            exit(1)

class ExceptionSafety(ExceptionSafetyNet):

    def __enter__(self):
        pass

    def __exit__(self, etype, value, traceback):
        return super().safety_net(etype, value, traceback)

class LmDriverSafety(ExceptionSafetyNet):
    
    def __exit__(self, etype, value, traceback):
        if value and isinstance(value, lm_drivers.LmDriverException):
            logger.exception(value)
            click.echo('LM error occured: {0}'.format(str(value)), err=True)
            exit(1)

def lm_driver_safety():
    return LmDriverSafety()
