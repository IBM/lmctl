import os
import logging.config
import yaml
from pkg_resources import resource_string

def setup_logging(default_level=logging.INFO):

  logging_config = resource_string("lmctllib.utils", 'logging.yaml')

  if logging_config is not None:
    config = yaml.safe_load(logging_config)
    logging.config.dictConfig(config)
  else:
    logging.basicConfig(level=default_level)	

