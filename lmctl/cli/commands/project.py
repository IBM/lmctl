import lmctl.cli.lifecycle as lifecycle_cli
import click
import logging
import os
import lmctl.project.package.core as pkgs
import lmctl.project.source.core as project_sources
import lmctl.project.source.creator as creator
import lmctl.project.types as project_types
import lmctl.files as files


logger = logging.getLogger(__name__)

######################################################
# Manage projects across environments
######################################################
@click.group(help='Commands for managing an Assembly/Resource Project')
def project():
    logger.debug('Project Management')


VALIDATE_HEADER = 'Validate'
BUILD_HEADER = 'Build'
PUSH_HEADER = 'Push'
TEST_HEADER = 'Test'
PULL_HEADER = 'Pull'
CREATE_HEADER = 'Create'
LIST_HEADER = 'List'


def exec_validate(controller, project):
    validate_options = project_sources.ValidateOptions()
    validate_options.journal_consumer = controller.consumer
    validation_result = controller.execute(project.validate, validate_options)
    controller.process_validation_result(validation_result)
    return validation_result


def exec_build(controller, project):
    build_options = project_sources.BuildOptions()
    build_options.journal_consumer = controller.consumer
    build_result = controller.execute(project.build, build_options)
    controller.process_validation_result(build_result.validation_result)
    return build_result


def exec_push(controller, pkg, env_sessions):
    push_options = pkgs.PushOptions()
    push_options.journal_consumer = controller.consumer
    return controller.execute(pkg.push, env_sessions, push_options)


def exec_test(controller, pkg_content, env_sessions):
    test_options = pkgs.TestOptions()
    test_options.journal_consumer = controller.consumer
    test_report = controller.execute(pkg_content.test, env_sessions, test_options)
    controller.process_test_report(test_report)


def exec_pull(controller, project, env_sessions):
    pull_options = project_sources.PullOptions()
    pull_options.journal_consumer = controller.consumer
    controller.execute(project.pull, env_sessions, pull_options)


@project.command(help='Validate sources of a Project')
@click.option('--project', 'project_path', default='./', help='File location of project')
def validate(project_path):
    """Validates an Assembly/Resource project"""
    logger.debug('Validating project at: {0}'.format(project_path))
    project = lifecycle_cli.open_project(project_path)
    controller = lifecycle_cli.ExecutionController(VALIDATE_HEADER)
    controller.start('{0} at {1}'.format(project.config.name, project_path))
    exec_validate(controller, project)
    controller.finalise()


@project.command(help='Build distributable package for Project')
@click.option('--project', 'project_path',  default='./', help='File location of project')
def build(project_path):
    """Builds an Assembly/Resource project"""
    logger.debug('Building project at: {0}'.format(project_path))
    project = lifecycle_cli.open_project(project_path)
    controller = lifecycle_cli.ExecutionController(BUILD_HEADER)
    controller.start('{0} at {1}'.format(project.config.name, project_path))
    exec_build(controller, project)
    controller.finalise()


@project.command(help='Push Project package to a LM environment')
@click.option('--project', 'project_path', default='./', help='File location of project')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload Resources must be provided')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def push(project_path, environment, config, armname, pwd):
    """Push an Assembly/Resource project"""
    logger.debug('Pushing project at: {0}'.format(project_path))
    project = lifecycle_cli.open_project(project_path)
    env_sessions = lifecycle_cli.build_sessions_for_project(project.config, environment, pwd, armname, config)
    controller = lifecycle_cli.ExecutionController(PUSH_HEADER)
    controller.start('{0} at {1}'.format(project.config.name, project_path))
    build_result = exec_build(controller, project)
    exec_push(controller, build_result.pkg, env_sessions)
    controller.finalise()


@project.command(help='Execute the Behaviour Tests of the Project')
@click.option('--project', 'project_path', default='./', help='File location of project')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload Resources to must be provided')
@click.option('--tests', default=None, help='specify individual tests to execute')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def test(project_path, environment, config, armname, tests, pwd):
    """Builds, pushes and runs the tests of an Assembly/Resource project on a target LM (and ARM) environment"""
    logger.debug('Testing project at: {0}'.format(project_path))
    project = lifecycle_cli.open_project(project_path)
    env_sessions = lifecycle_cli.build_sessions_for_project(project.config, environment, pwd, armname, config)
    controller = lifecycle_cli.ExecutionController(TEST_HEADER)
    controller.start('{0} at {1}'.format(project.config.name, project_path))
    build_result = exec_build(controller, project)
    pkg_content = exec_push(controller, build_result.pkg, env_sessions)
    exec_test(controller, pkg_content, env_sessions)
    controller.finalise()


@project.command(help='Pull contents of the Project resources from a LM environment')
@click.option('--project', 'project_path', default='./', help='File location of project')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config, without a password)')
def pull(project_path, environment, config, pwd):
    """Pulls the content of a Assembly/Resource from a target LM environment, overidding local content"""
    logger.debug('Pulling project at: {0}'.format(project_path))
    project = lifecycle_cli.open_project(project_path)
    env_sessions = lifecycle_cli.build_sessions_for_project(project.config, environment, pwd, None, config)
    controller = lifecycle_cli.ExecutionController(PULL_HEADER)
    controller.start('{0} at {1}'.format(project.config.name, project_path))
    exec_pull(controller, project, env_sessions)
    controller.finalise()

@project.command(help='List element(s) of a Project. Element options: tests')
@click.option('--project', 'project_path', default='./', help='File location of project')
@click.argument('element')
def list(project_path, element):
    logger.debug('Pulling elements of type {0} on project at: {1}'.format(element, project_path))
    project = lifecycle_cli.open_project(project_path)
    controller = lifecycle_cli.ExecutionController(LIST_HEADER)
    controller.start('{0} at {1}'.format(project.config.name, project_path))
    elements = controller.execute(project.list_elements, element)
    if len(elements) == 0:
        lifecycle_cli.printer.print_text('No tests')
    for element in elements:
        lifecycle_cli.printer.print_text('- {0}'.format(element))
    controller.finalise()

@project.command(help='Commands for creating starter Projects')
@click.argument('location', default='./')
@click.option('--name', help='Name of the Assembly/Resource managed in the project, by default the target directory name is used')
@click.option('--version', default='1.0', help='Version of the Assembly managed in the project')
@click.option('--type', 'project_type', default='Assembly', help='Type of service managed in the Project. Options: Assembly, NS (same as Assembly), VNF (same as Assembly), Resource')
@click.option('--rm', default='lm', help='Resource projects only - type of Resource Manager this Resource supports')
@click.option('--contains', nargs=2, type=click.Tuple([str, str]), multiple=True, help='Subprojects to initiate under this project. Must specify 2 values separated by spaces: type name. For a Resource subproject, you may set the rm by including it it in the type value using the format \'type::rm\' e.g. Resource::ansiblerm. If no rm is set then the value of the --rm option will be used instead')
@click.option('--servicetype', help='(Deprecated: use --type instead) type of Service managed in the Project (NS or VNF)')
@click.option('--vnfc', 'vnfcs', multiple=True, help='(Deprecated, use --contains instead) names of VNFCs (Resources) to initate under this project')
def create(location, name, version, project_type, rm, contains, servicetype, vnfcs):
    logger.debug('Project Create')
    if servicetype:
        if servicetype != project_type:
            project_type = servicetype
        lifecycle_cli.printer.print_text('Warning: --servicetype was set, you should use --type instead')
    project_request = __build_request_for_type(project_type)
    name = __process_name(location, name)
    project_request.name = name
    project_request.version = version
    project_request.target_location = location
    if isinstance(project_request, creator.CreateResourceProjectRequest):
        project_request.resource_manager = rm
    project_request.subproject_requests = __process_subprojects(contains, vnfcs, rm)
    create_options = creator.CreateOptions()
    create_options.journal_consumer = lifecycle_cli.ConsoleProjectJournalConsumer(lifecycle_cli.printer)
    try:
        creator.ProjectCreator(project_request, create_options).create()
    except creator.CreateError as e:
        lifecycle_cli.printer.print_text('Error: {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)


def __process_subprojects(subprojects, vnfcs, default_rm_type):
    subproject_requests = []
    rm = None
    for subproject in subprojects:
        project_type_ref, name = subproject
        if '::' in project_type_ref:
            ref_split = project_type_ref.split('::', 1)
            project_type = ref_split[0]
            rm = ref_split[1]
        else:
            project_type = project_type_ref
        request = __build_subproject_request_for_type(project_type)
        request.name = name
        request.directory = files.safe_file_name(name)
        if isinstance(request, creator.ResourceSubprojectRequest):
            if not rm:
                rm = default_rm_type
            request.resource_manager = rm
        subproject_requests.append(request)
    for vnfc in vnfcs:
        request = creator.ResourceSubprojectRequest()
        request.directory = files.safe_file_name(vnfc)
        request.resource_manager = creator.ANSIBLE_RM_TYPES[0]
        request.name = vnfc
        subproject_requests.append(request)
    return subproject_requests


def __build_request_for_type(project_type):
    if project_types.is_assembly_type(project_type):
        return creator.CreateAssemblyProjectRequest()
    elif project_types.is_resource_type(project_type):
        return creator.CreateResourceProjectRequest()
    else:
        lifecycle_cli.printer.print_text('Error: --type option must be one of: {0}'.format([project_types.ASSEMBLY_PROJECT_TYPE,
                                                                                            project_types.NS_PROJECT_TYPE, project_types.VNF_PROJECT_TYPE, project_types.RESOURCE_PROJECT_TYPE]))
        exit(1)


def __build_subproject_request_for_type(project_type):
    if project_types.is_assembly_type(project_type):
        return creator.AssemblySubprojectRequest()
    elif project_types.is_resource_type(project_type):
        return creator.ResourceSubprojectRequest()
    else:
        lifecycle_cli.printer.print_text('Error: --subproject option must include a type of: {0}'.format([project_types.ASSEMBLY_PROJECT_TYPE,
                                                                                                          project_types.NS_PROJECT_TYPE, project_types.VNF_PROJECT_TYPE, project_config.RESOURCE_PROJECT_TYPE]))
        exit(1)


def __process_name(target_location, name):
    if name is None:
        name = os.path.basename(target_location)
        if not name:
            name = os.path.basename(os.getcwd())
        lifecycle_cli.printer.print_text('Name not set, defaulting to: {0}'.format(name))
    return name
