import click 
import lmctllib.journal as journal
import lmctllib.config as lmctl_config
import lmctllib.project.lifecycle.execution as lifecycle_execution

ENV_NAME='ENV_NAME'
CONFIG_PATH='CONFIG_PATH'
LM_PWD='LM_PWD'

class ProjectEnvironmentConfigurator:

    def __init__(self):
        pass

    def get_environment(self, opts):
        if CONFIG_PATH in opts:
            configuration = lmctl_config.getConfig(opts[CONFIG_PATH])
        else:
            raise ValueError('No config path provided to the executor')
        if ENV_NAME in opts:
            env_name = opts[ENV_NAME] 
        else:
            raise ValueError('No environment name provided to the executor')
        def input_prompt(required_info, secret=False):
            if LM_PWD in opts and opts[LM_PWD] is not None:
                return opts[LM_PWD]
            else:
                return click.prompt('Please enter {0}'.format(required_info), hide_input=secret, default="")
        env = configuration.getConfiguredEnv(env_name, input_prompt)
        return env

class ProjectConsoleJournalConsumer(journal.Consumer):

    def __init__(self):
        self.__process_started = False

    def is_interested(self, entry: journal.Entry):
        return True

    def consume(self, entry: journal.Entry):
        if isinstance(entry, journal.OpenChapterEntry):
            self.__handle_open_chapter(entry)
        elif isinstance(entry, journal.CloseChapterEntry):
            self.__handle_close_chapter(entry)
        elif isinstance(entry, journal.ParagraphBreakEntry):
            self.__break()
        else:
            click.echo(entry.to_readable())

    def __handle_open_chapter(self, entry: journal.OpenChapterEntry):
        if entry.chapter_name is lifecycle_execution.JRNL_CHAPTER_EXEC_START or entry.chapter_name is lifecycle_execution.JRNL_CHAPTER_EXEC_END:
            self.__exec_chapter_opening()
        else:
            self.__new_section(entry)

    def __handle_close_chapter(self, entry: journal.CloseChapterEntry):
        if entry.chapter_name is lifecycle_execution.JRNL_CHAPTER_EXEC_START or entry.chapter_name is lifecycle_execution.JRNL_CHAPTER_EXEC_END:
            self.__exec_chapter_closing()
        else:
            self.__break()

    def __new_section(self, entry: journal.OpenChapterEntry):
        click.echo('--> {0}'.format(entry.chapter_name))

    def __exec_chapter_opening(self):
        click.echo('===========================================')

    def __exec_chapter_closing(self):
        click.echo('===========================================')

    def __break(self):
        click.echo('')
