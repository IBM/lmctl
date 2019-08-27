import lmctl.project.handlers.interface as handlers_api

class PushProcessError(Exception):
    pass

class PushProcess:

    def __init__(self, pkg_content, options, journal, env_sessions):
        self.pkg_content = pkg_content
        self.journal = journal
        self.options = options
        self.env_sessions = env_sessions

    def execute(self):
        return PushWorker(self.pkg_content, self.options, self.journal, self.env_sessions).work()

class PushWorker:

    def __init__(self, pkg_content, options, journal, env_sessions):
        self.pkg_content = pkg_content
        self.journal = journal
        self.options = options
        self.env_sessions = env_sessions

    def work(self):
        self.__push_child_content()
        self.__push_content()

    def __push_content(self):
        self.journal.section('Push Content')
        try:
            self.pkg_content.handler.push_content(self.journal, self.env_sessions)
        except handlers_api.ContentHandlerError as e:
            raise PushProcessError(str(e)) from e

    def __push_child_content(self):
        subcontents = self.pkg_content.subcontents
        for subcontent in subcontents:
            self.journal.subproject(subcontent.meta.name)
            PushWorker(subcontent, self.options, self.journal, self.env_sessions).work()
            self.journal.subproject_end(subcontent.meta.name)

