import os
import yaml
import logging
import shutil
import traceback
import tempfile
import tarfile
import lmctllib.journal as journal
import lmctllib.pipeline as pipeline
import lmctllib.project.model as project_model
import lmctllib.project.structure as project_struct
import lmctllib.project.packaging as project_packaging
import lmctllib.project.lifecycle.tasks as lifecycle_task
import lmctllib.project.lifecycle.tasks.packaging as packaging_tasks
import lmctllib.project.lifecycle.tasks.pulling as pull_tasks
import lmctllib.project.lifecycle.tasks.pushing as push_tasks
import lmctllib.project.lifecycle.tasks.structure as struct_tasks
import lmctllib.project.lifecycle.tasks.testing as testing_tasks
import lmctllib.project.lifecycle.tasks.validation as validation_tasks

logger = logging.getLogger(__name__)


class ExecutionException(Exception):
    pass


class LifecyclePipelines:

    def __init__(self):
        self.pipelines = {}
        self.upstream_dependencies = {}

    def addPipeline(self, pipeline):
        self.pipelines[pipeline.task_name] = pipeline

    def addPipelineUpstreamDependency(self, pipeline_name, upstream_dependency):
        self.__getPipeline(pipeline_name)
        self.__getPipeline(upstream_dependency.upstream_pipeline_name)

        if pipeline_name not in self.upstream_dependencies:
            self.upstream_dependencies[pipeline_name] = []
        self.upstream_dependencies[pipeline_name].append(upstream_dependency)

    def __getPipeline(self, pipeline_name):
        if pipeline_name not in self.pipelines:
            raise ValueError('No pipeline with name: {0}'.format(pipeline_name))
        return self.pipelines[pipeline_name]

    def getExecutionOrderForPipeline(self, target_pipeline_name, conditions):
        return self.__getPipelineDependencies(target_pipeline_name, conditions)

    def __getPipelineDependencies(self, target_pipeline_name, conditions):
        target_pipeline = self.__getPipeline(target_pipeline_name)
        pipelines = []
        if target_pipeline_name in self.upstream_dependencies:
            dependencies = self.upstream_dependencies[target_pipeline_name]
            for dependency in dependencies:
                if dependency.include(conditions) is True:
                    upstream_pipeline = self.__getPipeline(dependency.upstream_pipeline_name)
                    pipelines.extend(self.__getPipelineDependencies(upstream_pipeline.task_name, conditions))
        pipelines.append(target_pipeline)
        return pipelines


class UpstreamDependency:

    def __init__(self, upstream_pipeline_name, condition_predicate):
        self.upstream_pipeline_name = upstream_pipeline_name
        self.condition_predicate = condition_predicate

    def include(self, conditions):
        if self.condition_predicate is not None:
            return self.condition_predicate(conditions)
        return True


class Predicates:
    @staticmethod
    def isTrue(condition_key):
        def new_condition(conditions):
            return condition_key in conditions and conditions[condition_key] is True
        return new_condition

    @staticmethod
    def isFalse(condition_key):
        def new_condition(conditions):
            return condition_key not in conditions or conditions[condition_key] is False
        return new_condition


build_pipeline_tasks = [
    struct_tasks.CleanBuildDirectory(),
    validation_tasks.ValidateVnfcDirectories(),
    packaging_tasks.PackageVnfcs(),
    packaging_tasks.PackageServiceDescriptor(),
    packaging_tasks.PackageServiceBehaviours(),
    packaging_tasks.FinalPackage()
]
build_pipeline = pipeline.Pipeline("Build Stage", build_pipeline_tasks)

push_pipeline_tasks = [
    struct_tasks.CleanPushDirectory(),
    packaging_tasks.ExtractBuildPackage(),
    push_tasks.DeployVnfcs(),
    push_tasks.DeployServiceDescriptor(),
    push_tasks.DeployServiceBehaviours()
]
push_pipeline = pipeline.Pipeline("Push Stage", push_pipeline_tasks)

test_pipeline_tasks = [
    testing_tasks.RunBehaviourTests()
]
test_pipeline = pipeline.Pipeline("Test Stage", test_pipeline_tasks)

pull_pipeline_tasks = [
    struct_tasks.CleanBackupDirectory(),
    pull_tasks.PullServiceDescriptor(),
    pull_tasks.PullServiceBehaviours()
]
pull_pipeline = pipeline.Pipeline("Pull Stage", pull_pipeline_tasks)

SKIP_BUILD_CONDITION = 'skip_build'
SKIP_PUSH_CONDITION = 'skip_push'

lifecycle_pipelines = LifecyclePipelines()
lifecycle_pipelines.addPipeline(build_pipeline)
lifecycle_pipelines.addPipeline(push_pipeline)
lifecycle_pipelines.addPipeline(test_pipeline)
lifecycle_pipelines.addPipeline(pull_pipeline)

lifecycle_pipelines.addPipelineUpstreamDependency(push_pipeline.task_name, UpstreamDependency(build_pipeline.task_name, Predicates.isFalse(SKIP_BUILD_CONDITION)))
lifecycle_pipelines.addPipelineUpstreamDependency(test_pipeline.task_name, UpstreamDependency(push_pipeline.task_name, Predicates.isFalse(SKIP_PUSH_CONDITION)))

EXECUTOR_OPTIONS = {}

EXEC_OPTS_ARM_NAME = 'ARM_NAME'
EXEC_OPTS_ENV = 'ENV'
EXEC_OPTS_SELECTED_TESTS = 'SELECTED_TESTS'
EXEC_OPTS_PKG_PATH = 'PKG_PATH'
EXEC_OPTS_SKIP_BUILD = 'SKIP_BUILD'
EXEC_OPTS_SKIP_PUSH = 'SKIP_PUSH'

JRNL_CHAPTER_EXEC_START = 'ExecStart'
JRNL_CHAPTER_EXEC_END = 'ExecEnd'


class ExecutionResult:
    def __init__(self, passed, details):
        self.passed = passed
        self.details = details


class ProjectLifecycleExecutor:

    def __init__(self, project_path, journal_consumer=None):
        self.project = None
        if not project_path:
            raise Exception('Must specify a project_path')
        self.project_path = project_path

        project_tree = project_struct.ProjectTree(self.project_path)
        self.project_file = project_tree.projectFile()
        if not os.path.exists(self.project_file):
            logger.info('Could not find project file at: {0}'.format(self.project_file))
            logger.info('Creating default project file based on current directory structure')
            project_init = project_struct.ProjectFileCreator(self.project_path)
            project_init.makeFile()

        if os.path.exists(self.project_file):
            with open(self.project_file, 'rt') as f:
                raw_project = yaml.safe_load(f.read())
                if not raw_project:
                    raw_project = {}
                self.__parseProject(raw_project)
        else:
            raise Exception('Could not find project file at: {0}'.format(self.project_file))

        self.journal = journal.Journal()
        if journal_consumer is not None:
            self.journal.register_consumer(journal_consumer)

    def __parseProject(self, raw_project):
        self.project = project_model.ProjectParser(raw_project).parse()

    def __prepare_pipeline(self, pipeline_name, pipeline_task_name, executor_options):
        conditions = {}
        if EXEC_OPTS_SKIP_BUILD in executor_options and executor_options[EXEC_OPTS_SKIP_BUILD] is True:
            conditions[SKIP_BUILD_CONDITION] = True
        if EXEC_OPTS_SKIP_PUSH in executor_options and executor_options[EXEC_OPTS_SKIP_PUSH] is True:
            conditions[SKIP_PUSH_CONDITION] = True
        pipelines = lifecycle_pipelines.getExecutionOrderForPipeline(pipeline_task_name, conditions)
        entry_pipeline = pipeline.Pipeline(pipeline_name, pipelines)
        return entry_pipeline

    def __prepare_tools(self, executor_options):
        init_tools = {}
        if EXEC_OPTS_ENV in executor_options:
            init_tools[lifecycle_task.TOOL_ENVIRONMENT] = executor_options[EXEC_OPTS_ENV]
        init_tools[lifecycle_task.TOOL_ENVIRONMENT_SELECTORS] = self.__gather_environment_selectors(executor_options)
        init_tools[lifecycle_task.TOOL_EVENT_LOG] = self.journal
        init_tools[lifecycle_task.TOOL_PROJECT] = self.project
        init_tools[lifecycle_task.TOOL_PROJECT_NAME] = self.project.name
        init_tools[lifecycle_task.TOOL_PROJECT_TREE] = project_struct.ProjectTree(self.project_path)
        task_tools = pipeline.TaskTools(init_tools)
        return task_tools

    def __prepare_products(self, executor_options):
        init_products = {}
        if EXEC_OPTS_PKG_PATH in executor_options:
            init_products[lifecycle_task.PRODUCT_PKG_PATH] = executor_options[EXEC_OPTS_PKG_PATH]
        if EXEC_OPTS_SELECTED_TESTS in executor_options:
            init_products[lifecycle_task.PRODUCT_SELECTED_TESTS] = executor_options[EXEC_OPTS_SELECTED_TESTS]
        products = pipeline.TaskProducts(init_products)
        return products

    def __gather_environment_selectors(self, executor_options):
        environment_selectors = {}
        if EXEC_OPTS_ARM_NAME in executor_options:
            environment_selectors[project_packaging.ENV_SELECTOR_ARM_NAME] = executor_options[EXEC_OPTS_ARM_NAME]
        return environment_selectors

    def __execute_pipeline(self, pipeline_name, pipeline_task_name, executor_options):
        executable_pipeline = self.__prepare_pipeline(pipeline_name, pipeline_task_name, executor_options)
        tools = self.__prepare_tools(executor_options)
        products = self.__prepare_products(executor_options)

        self.journal.open_chapter(JRNL_CHAPTER_EXEC_START)
        self.journal.add_text('{0}: {1} at {2}'.format(pipeline_name, self.project.name, self.project_path))
        self.journal.close_chapter()
        execution_result = executable_pipeline.execute(tools, products)
        return self.__process_execution_result(pipeline_name, execution_result)

    def __process_execution_result(self, pipeline_name, result):
        self.journal.open_chapter(JRNL_CHAPTER_EXEC_END)
        passed = result.code == pipeline.ResultCode.PASSED
        detail = result.report()
        self.journal.add_text(detail)
        self.journal.close_chapter()
        return ExecutionResult(passed, detail)

    def build(self, executor_options=None):
        if executor_options is None:
            executor_options = {}
        return self.__execute_pipeline("Build", build_pipeline.task_name, executor_options)

    def push(self, executor_options=None):
        if executor_options is None:
            executor_options = {}
        return self.__execute_pipeline("Push", push_pipeline.task_name, executor_options)

    def test(self, executor_options=None):
        if executor_options is None:
            executor_options = {}
        return self.__execute_pipeline("Test", test_pipeline.task_name, executor_options)

    def pull(self, executor_options=None):
        if executor_options is None:
            executor_options = {}
        return self.__execute_pipeline("Pull", pull_pipeline.task_name, executor_options)

    def list(self, element, executor_options=None):
        if executor_options is None:
            executor_options = {}
        if element == 'tests':
            tools = self.__prepare_tools(executor_options)
            testing_tasks.ListBehaviourTests().execute(tools, pipeline.TaskProducts())


class PackagedProjectExpander:

    def __init__(self):
        pass

    def expand(self, pkg_path):
        project_tree = self.__buildProjectFromPkg(pkg_path)
        return project_tree.directory()

    def __buildProjectFromPkg(self, pkg_path):
        tmp_project_dir = os.path.join(tempfile.gettempdir(), 'lmctlproj')
        if os.path.exists(tmp_project_dir):
            shutil.rmtree(tmp_project_dir)
        os.makedirs(tmp_project_dir)

        logger.info('Extracting package {0} to working directory {1}'.format(pkg_path, tmp_project_dir))

        project_tree = project_struct.ProjectTree(tmp_project_dir)
        package_tree = project_struct.PackageWrapperTree(tmp_project_dir)
        if os.path.exists(pkg_path):
            with tarfile.open(pkg_path, mode='r:gz') as pkg_tar:
                pkg_tar.extract(os.path.basename(package_tree.projectFile()), path=os.path.dirname(project_tree.projectFile()))
        else:
            logger.error('Package not found: {0}'.format(pkg_path))
            exit(1)

        if not os.path.exists(project_tree.projectFile()):
            logger.error('Invalid package - does not include a project file')

        return project_tree
