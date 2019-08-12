import click
import sys
import logging
import lmctllib.config as lmctl_config

logger = logging.getLogger(__name__)

######################################################
# env command line functions
######################################################

@click.group(help='Commands for inspecting available LM environments')
def env():
  logger.debug('Environments')

@env.command(help='List available LM environments')
@click.option('--config', default=None, help='path to lmctl configuration file')
def list(config):
  """List available environments"""
  config=lmctl_config.getConfig(config)
  logger.info('Available environments:')
  if config.environments is not None:
    for i in config.environments:
      if config.environments[i].description:
        logger.info('\t- '+i+': '+config.environments[i].description)
      else:
      	logger.info('\t- '+i)
 