import abc
import traceback
import logging
import lmctllib.pipeline as pipeline
import lmctllib.journal as journal

logger = logging.getLogger(__name__)

TOOL_PROJECT_TREE = "ProjectTree"
TOOL_EVENT_LOG = "EventLog"
TOOL_ENVIRONMENT = "Environment"
TOOL_ENVIRONMENT_SELECTORS = "EnvironmentSelectors"
TOOL_PROJECT_NAME = "ProjectName"
TOOL_PROJECT = "Project"

PRODUCT_PKG_PATH = "PackagePath"
PRODUCT_SELECTED_TESTS = "SelectedTests"

class ProjectLifecycleTaskExecutionException(Exception):
    pass

class ProjectLifecycleTask(pipeline.Task, abc.ABC):

    def __init__(self, task_name):
        super().__init__(task_name)

    def execute(self, tools: pipeline.TaskTools, products: pipeline.TaskProducts):
        self.__tools = tools
        self.__products = products
        event_journal = self._get_journal()
        event_journal.open_chapter(self.task_name)
        result = None
        try:
            result = self.execute_work(tools, products)
        except Exception as e:
            logger.error(traceback.format_exc())
            result = self._return_failure(str(e))
        event_journal.close_chapter()
        return result

    @abc.abstractmethod
    def execute_work(self, tools: pipeline.TaskTools, products: pipeline.TaskProducts):
        pass

    def _get_project_tree(self):
        project_tree = self.__tools.get_tool(TOOL_PROJECT_TREE)
        return project_tree

    def _get_project(self):
        project = self.__tools.get_tool(TOOL_PROJECT)
        return project

    def _get_journal(self):
        event_log = self.__tools.get_tool(TOOL_EVENT_LOG)
        return event_log

    def _get_environment(self):
        environment = self.__tools.get_tool(TOOL_ENVIRONMENT)
        return environment

    def _get_environment_selectors(self):
        environment_selector = self.__tools.get_tool(TOOL_ENVIRONMENT_SELECTORS)
        return environment_selector

    def _get_project_name(self):
        project_name = self.__tools.get_tool(TOOL_PROJECT_NAME)
        return project_name

    def _return_failure(self, failure_reason):
        decorated_reason = "Error: {0}".format(failure_reason)
        self._get_journal().add_text(decorated_reason, journal.EntryTarget.CONTENT, journal.EntryType.ERROR)
        return pipeline.TaskResult.failed(self.task_name, [decorated_reason])

    def _return_passed(self):
        return pipeline.TaskResult.passed(self.task_name)

    def _return_skipped(self, skipped_reason):
        self._get_journal().add_text(skipped_reason, journal.EntryTarget.CONTENT, journal.EntryType.WARNING)
        return pipeline.TaskResult.skipped(self.task_name, [skipped_reason])

class ExampleTask(ProjectLifecycleTask):

    def __init__(self, task_name):
        super().__init__(task_name)

    def execute_work(self, tools: pipeline.TaskTools, products: pipeline.TaskProducts):
        project_tree = self._get_project_tree()
        print("\n\tThis is an example task")
        print("\n\t{0}".format(project_tree.directory()))
