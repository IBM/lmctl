import click
import logging
import lmctllib.project.lifecycle.execution as lifecycle_execution
from .utils import ProjectConsoleJournalConsumer, ProjectEnvironmentConfigurator, ENV_NAME, CONFIG_PATH, LM_PWD

logger = logging.getLogger(__name__)


@click.group(help='Commands for managing a package built from a NS/VNF Project')
def pkg():
    logger.debug('Package Management')


def __run_executor(execute_func, *args):
    try:
        result = execute_func(*args)
    except lifecycle_execution.ExecutionException as e:
        click.echo('ERROR: {0}'.format(str(e)), err=True)
        exit(1)
    if result.passed is False:
        exit(1)


@pkg.command(help='Push a previously built package to a LM environment')
@click.argument('package')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload VNFCs to must be provided')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def push(package, environment, config, armname, pwd):
    """Pushes an existing NS/VNF package to a target LM (and ARM) environment"""
    logger.debug('Pushing package at: {0}'.format(package))
    expander = lifecycle_execution.PackagedProjectExpander()
    project_path = expander.expand(package)
    env_configurator = ProjectEnvironmentConfigurator()
    configured_env = env_configurator.get_environment({ENV_NAME: environment, CONFIG_PATH: config, LM_PWD: pwd})
    executor_options = {}
    executor_options[lifecycle_execution.EXEC_OPTS_ARM_NAME] = armname
    executor_options[lifecycle_execution.EXEC_OPTS_ENV] = configured_env
    executor_options[lifecycle_execution.EXEC_OPTS_PKG_PATH] = package
    executor_options[lifecycle_execution.EXEC_OPTS_SKIP_BUILD] = True
    project_executor = lifecycle_execution.ProjectLifecycleExecutor(project_path, ProjectConsoleJournalConsumer())
    __run_executor(project_executor.push, executor_options)
