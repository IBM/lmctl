import lmctl.journal as journal


class ProjectJournal:

    def __init__(self, journal_consumer=None):
        self.journal = journal.Journal()
        if journal_consumer is not None:
            self.journal.register_consumer(journal_consumer)
        self.journal.open_chapter('Start')

    def subproject(self, sub_project_name):
        self.journal.add_entry(SubprojectEvent(sub_project_name))

    def subproject_end(self, sub_project_name):
        self.journal.add_entry(SubprojectEndEvent(sub_project_name))

    def section(self, title):
        self.journal.add_entry(SectionEvent(title))

    def stage(self, title):
        self.journal.add_entry(StageEvent(title))

    def event(self, message):
        self.journal.add_entry(Event(message))

    def error_event(self, message):
        self.journal.add_entry(Event(message, journal.EntryType.ERROR))


class ProjectEvent(journal.Entry):
    pass


class SubprojectEvent(ProjectEvent):

    def __init__(self, sub_project_name):
        super().__init__(journal.EntryTarget.CONTENT, journal.EntryType.NORMAL)
        self.sub_project_name = sub_project_name

    def to_readable(self):
        return self.sub_project_name


class SubprojectEndEvent(ProjectEvent):

    def __init__(self, sub_project_name):
        super().__init__(journal.EntryTarget.CONTENT, journal.EntryType.NORMAL)
        self.sub_project_name = sub_project_name

    def to_readable(self):
        return self.sub_project_name


class SectionEvent(ProjectEvent):

    def __init__(self, title):
        super().__init__(journal.EntryTarget.CONTENT, journal.EntryType.NORMAL)
        self.title = title

    def to_readable(self):
        return self.title


class StageEvent(ProjectEvent):

    def __init__(self, title):
        super().__init__(journal.EntryTarget.CONTENT, journal.EntryType.NORMAL)
        self.title = title

    def to_readable(self):
        return self.title


class Event(ProjectEvent):

    def __init__(self, message, format=journal.EntryType.NORMAL):
        super().__init__(journal.EntryTarget.CONTENT, format)
        self.message = message

    def to_readable(self):
        return self.message
