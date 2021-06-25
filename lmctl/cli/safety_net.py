import click 
import logging
from typing import List
from lmctl.cli.io import IOController
from lmctl.client import TNCOClientError
from lmctl.drivers.lm.base import LmDriverException
from lmctl.drivers.arm import AnsibleRmDriverException

logger = logging.getLogger(__name__)

class ExceptionSafetyNet:
    
    def __init__(self, catchable_exceptions: List = None, error_prefix: str = 'Error: ', io_controller: IOController = None):
        self.catchable_exceptions = catchable_exceptions
        self.io_controller = io_controller if io_controller is not None else IOController.get()
        self.error_prefix = error_prefix

    def __enter__(self):
        pass

    def __exit__(self, etype, value, traceback):
        if value and any(isinstance(value, e) for e in self.catchable_exceptions):
            logger.exception(value)
            self.io_controller.print_error(f'{self.error_prefix}{value}')
            if hasattr(value, 'exit_code'):
                exit(value.exit_code)
            else:
                exit(1)

def safety_net(*catchable_exceptions, error_prefix: str = 'Error: ', io_controller: IOController = None):
    if len(catchable_exceptions) == 0:
        catchable_exceptions = [Exception]
    return ExceptionSafetyNet(catchable_exceptions, error_prefix=error_prefix, io_controller=io_controller)

def tnco_client_safety_net(*extra_exceptions, io_controller: IOController = None):
    exceptions = [TNCOClientError]
    exceptions.extend(extra_exceptions)
    return safety_net(*exceptions, error_prefix='TNCO error occurred: ', io_controller=io_controller)

def lm_driver_safety_net(io_controller: IOController = None):
    return safety_net(LmDriverException, AnsibleRmDriverException, TNCOClientError, error_prefix='TNCO error occurred: ', io_controller=io_controller)