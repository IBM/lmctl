import lmctl.project.handlers.interface as handlers_api

TEST_ELEMENT_TYPE = 'tests'

class ListElementProcessError(Exception):
    pass

class ListElementProcess:

    def __init__(self, project, journal, element_type):
        self.project = project
        self.journal = journal
        if element_type != TEST_ELEMENT_TYPE:
            raise ListElementProcessError('Cannot list elements of unsupported type: {0}'.format(element_type))
        self.element_type = handlers_api.ELEMENT_TYPE_TESTS
    
    def execute(self):
        return ListElementWorker(self.project, self.journal, self.element_type).work()

class ListElementWorker:

    def __init__(self, project, journal, element_type):
        self.project = project
        self.journal = journal
        self.element_type = element_type

    def work(self):
        all_elements = []
        try:
            source_elements = self.project.source_handler.list_elements(self.journal, self.element_type)
        except handlers_api.SourceHandlerError as e:
            raise ListElementProcessError(str(e)) from e
        all_elements.extend(source_elements)
        self.__gather_child_project_elements(all_elements)
        return all_elements

    def __gather_child_project_elements(self, elements):
        for subproject in self.project.subprojects:
            sub_elements = ListElementWorker(subproject, self.journal, self.element_type).work()
            elements.extend(sub_elements)
