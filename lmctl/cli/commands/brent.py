import click
import logging
import os

logger = logging.getLogger(__name__)

######################################################
# Manage Brent RM drivers
######################################################
@click.group(help='Commands for managing Brent Resource Manager')
def brent():
    logger.debug('Brent Resource Manager')

@brent.command(help='Add a VIM driver to Brent')
@click.argument('environment')
@click.option('--type', default='Openstack', help='Infrastructure type')
@click.option('--url', help='url of VIM driver to add to Brent')
def addvimdriver(environment, type, url):
    """Add a VIM driver"""

@brent.command(help='Add a lifecycle driver to Brent')
@click.argument('environment')
@click.option('--url', help='url of lifecycle driver to add to Brent')
def addlifecycledriver(environment, url):
    """Add a lifecycle driver"""

@brent.command(help='Remove a Brent driver')
@click.argument('environment')
def removedriver(environment):
    """Remove a driver from Brent"""

@brent.command(help='List all Brent drivers')
@click.argument('environment')
def listdrivers(environment):
    """List all Brent drivers"""
