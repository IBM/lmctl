import enum
import abc
import traceback
import logging

logger = logging.getLogger(__name__)

@enum.unique
class ResultCode(enum.Enum):
    FAILED = 30
    SKIPPED = 20
    PASSED = 10

class TaskResult:

    def __init__(self, task_name: str, code: ResultCode, remarks: list=[]):
        if not task_name:
            raise ValueError('Task name not defined')
        if not code:
            raise ValueError('Code not defined')
        self.__task_name = task_name
        self.__code = code
        if remarks is None:
            remarks = []
        self.__remarks = remarks

    @property
    def task_name(self):
        return self.__task_name

    @property
    def code(self):
        return self.__code

    @property
    def remarks(self):
        return self.__remarks

    def report(self, indent=0):
        indent_str = ""
        for i in range(indent):
            indent_str += "    "
        report = "{0}{1} - {2}".format(indent_str, self.__task_name, self.__code.name)
        if len(self.__remarks) > 0:
            report += ": "
            for remark in self.__remarks:
                for idx, line in enumerate(remark.splitlines()):
                    report += "\n{0}    ".format(indent_str)
                    report += line
        return report

    @staticmethod
    def failed(task_name, remarks=[]):
        if remarks is None:
            remarks = []
        if len(remarks)==0:
            remarks.append('Failure reason not given')
        return TaskResult(task_name, ResultCode.FAILED, remarks)

    @staticmethod
    def skipped(task_name, remarks=[]):
        return TaskResult(task_name, ResultCode.SKIPPED, remarks)

    @staticmethod
    def passed(task_name, remarks=[]):
        return  TaskResult(task_name, ResultCode.PASSED, remarks)

class TaskProducts:

    def __init__(self, state=None):
        if state is None:
            state = {}
        self.__state = state

    def set_value(self, key, value):
        self.__state[key] = value

    def get_optional_value(self, key):
        if key in self.__state:
            return self.__state[key]

    def get_value(self, key):
        if key in self.__state:
            return self.__state[key]
        else:
            raise ValueError('No value found with key: {0}'.format(key))

    def has_value(self, key):
        return key in self.__state and self.__state[key] is not None

class TaskTools:

    def __init__(self, tools=None):
        if tools is None:
            tools = {}
        self.__tools = tools

    def get_tool(self, name):
        if name in self.__tools:
            return self.__tools[name]
        else:
            raise ValueError('No task tool found with name: {0}'.format(name))

class Task(abc.ABC):

    def __init__(self, task_name):
        self.__task_name = task_name

    @property
    def task_name(self):
        return self.__task_name

    @abc.abstractmethod
    def execute(self, tools: TaskTools, products: TaskProducts):
        return TaskResult.skipped(self.task_name, ['Not implemented'])

class WorkerTask(Task):

    def __init__(self, task_name, work):
        if not work:
            raise ValueError('A work function must be provided to a Worker Task')
        if not callable(work):
            raise ValueError('Work function provided to Worker Task must be a callable function but got a: {0}'.format(type(work).__name__))
        self.__work = work
        super().__init__(task_name)

    def execute(self, tools: TaskTools, products: TaskProducts):
        try:
            task_result = self.__work(self.task_name, tools, products)
        except Exception as e:
            logger.error(traceback.format_exc())
            return TaskResult.failed(self.task_name, [str(e)])
        if task_result:
            if task_result.task_name is not self.task_name:
                raise ValueError('Worker Task functions should not return a TaskResult with an alternative task name: expected={0}, got={1}'.format(self.task_name, task_result.task_name))
            return task_result
        else:
            return TaskResult.passed(self.task_name)

class Pipeline(Task):

    def __init__(self, task_name, tasks, **kwargs):
        self.__tasks = tasks
        if 'full_report' in kwargs:
            self.__full_report = kwargs['full_report']
        else:
            self.__full_report = False
        super().__init__(task_name)

    def execute(self, tools: TaskTools, products: TaskProducts=TaskProducts()):
        task_results = []
        for task in self.__tasks:
            task_result = task.execute(tools, products)
            if task_result.code is ResultCode.FAILED:
                return TaskResult.failed(self.task_name, [task_result.report()])
            if self.__full_report:
                task_results.append(task_result.report())
        return TaskResult.passed(self.task_name, task_results)
