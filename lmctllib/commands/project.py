import click
import logging
import lmctllib.project.structure as project_struct
import lmctllib.project.lifecycle.execution as lifecycle_execution
from .utils import ProjectConsoleJournalConsumer, ProjectEnvironmentConfigurator, ENV_NAME, CONFIG_PATH, LM_PWD

logger = logging.getLogger(__name__)

######################################################
# Manage projects across environments
######################################################
@click.group(help='Commands for managing a NS/VNF Project')
def project():
    logger.debug('Project Management')


def __run_executor(execute_func, *args):
    try:
        result = execute_func(*args)
    except lifecycle_execution.ExecutionException as e:
        click.echo('ERROR: {0}'.format(str(e)), err=True)
        exit(1)
    if result.passed is False:
        exit(1)


@project.command(help='Create a new Project in a target directory')
@click.argument('location', default='./')
@click.option('--name', help='Name of the Servce managed in the project, by default the target directory name is used')
@click.option('--version', default='1.0', help='Version of the Service managed in the Project')
@click.option('--servicetype', default='NS', help='Type of Service managed in the Project (NS or VNF)')
@click.option('--vnfc', multiple=True, help='Names of VNFCs to initate')
def create(location, name, version, servicetype, vnfc):
    """Creates the basic directory structure and files for a NS/VNF project"""
    request = project_struct.ProjectCreateRequest()
    request.name = name
    request.target_location = location
    request.serviceType = servicetype
    request.version = version
    request.vnfcs = vnfc
    creator = project_struct.ProjectCreator()
    creator.create(request)


@project.command(help='Build distributable package for Project')
@click.argument('project', default='./')
def build(project):
    """Builds a NS/VNF project"""
    logger.debug('Building project at: {0}'.format(project))
    project_executor = lifecycle_execution.ProjectLifecycleExecutor(project, ProjectConsoleJournalConsumer())
    __run_executor(project_executor.build)


@project.command(help='Push Project package to a LM environment')
@click.option('--project', default='./')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload VNFCs to must be provided')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def push(project, environment, config, armname, pwd):
    """Builds and pushes a NS/VNF project to a target LM (and ARM) environment"""
    logger.debug('Pushing project at: {0}'.format(project))
    env_configurator = ProjectEnvironmentConfigurator()
    configured_env = env_configurator.get_environment({ENV_NAME: environment, CONFIG_PATH: config, LM_PWD: pwd})
    executor_options = {}
    executor_options[lifecycle_execution.EXEC_OPTS_ARM_NAME] = armname
    executor_options[lifecycle_execution.EXEC_OPTS_ENV] = configured_env
    project_executor = lifecycle_execution.ProjectLifecycleExecutor(project, ProjectConsoleJournalConsumer())
    __run_executor(project_executor.push, executor_options)


@project.command(help='Execute the Behaviour Tests of the Project')
@click.option('--project', default='./')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload VNFCs to must be provided')
@click.option('--tests', default=None, help='specify individual tests to execute')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def test(project, environment, config, armname, tests, pwd):
    """Builds, pushes and runs the tests of a NS/VNF project on a target LM (and ARM) environment"""
    logger.debug('Testing project at: {0}'.format(project))
    env_configurator = ProjectEnvironmentConfigurator()
    configured_env = env_configurator.get_environment({ENV_NAME: environment, CONFIG_PATH: config, LM_PWD: pwd})
    executor_options = {}
    executor_options[lifecycle_execution.EXEC_OPTS_ARM_NAME] = armname
    executor_options[lifecycle_execution.EXEC_OPTS_ENV] = configured_env
    executor_options[lifecycle_execution.EXEC_OPTS_SELECTED_TESTS] = tests
    project_executor = lifecycle_execution.ProjectLifecycleExecutor(project, ProjectConsoleJournalConsumer())
    __run_executor(project_executor.test, executor_options)


@project.command(help='List element(s) of a Project. Element options: tests')
@click.option('--project', default='./')
@click.argument('element')
def list(project, element):
    """Lists elements of a NS/VNF Project"""
    logger.debug('Listing element {0} of project: {1}'.format(element, project))
    project_executor = lifecycle_execution.ProjectLifecycleExecutor(project, ProjectConsoleJournalConsumer())
    __run_executor(project_executor.list, element)


@project.command(help='Pull contents of the Project resources from a LM environment')
@click.option('--project', default='./')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config, without a password)')
def pull(project, environment, config, pwd):
    """Pulls the content of a NS/VNF Project from a target LM (and ARM) environment, overidding local content"""
    logger.debug('Pulling project at: {0}'.format(project))
    env_configurator = ProjectEnvironmentConfigurator()
    configured_env = env_configurator.get_environment({ENV_NAME: environment, CONFIG_PATH: config, LM_PWD: pwd})
    executor_options = {}
    executor_options[lifecycle_execution.EXEC_OPTS_ENV] = configured_env
    project_executor = lifecycle_execution.ProjectLifecycleExecutor(project, ProjectConsoleJournalConsumer())
    __run_executor(project_executor.pull, executor_options)
