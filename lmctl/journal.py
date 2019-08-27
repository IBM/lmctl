import abc
import enum

@enum.unique
class EntryTarget(enum.Enum):
    """
    Indicates the target of an Entry, to highlight if it is important or just a "side" piece of information. Similar to the "level" concept in logging frameworks
    """
    CONTENT = 40
    SIDENOTE = 30
    FOOTNOTE = 20

@enum.unique
class EntryType(enum.Enum):
    """
    Indicates the format of an Entry. Allows Entries to indicate they feature content of a particular type
    """
    ERROR = "Error"
    WARNING = "Warning"
    NORMAL = "Normal"

class Entry(abc.ABC):
    """
    A single piece of information added to the Journal
    """
    def __init__(self, entry_target: EntryTarget, entry_type: EntryType):
        self.__entry_target = entry_target
        self.__entry_type = entry_type

    @abc.abstractmethod
    def to_readable(self):
        """
        This Entry as a human readable string

        Returns:
            str: the Entry as a human readable string        
        """
        pass

    @property
    def entry_target(self):
        """
        This target for this Entry

        Returns:
            EntryTarget: the target for this Entry    
        """
        return self.__entry_target

    @property
    def entry_type(self):
        """
        The type of this Entry

        Returns:
            EntryType: the type of this Entry    
        """
        return self.__entry_type

class Consumer(abc.ABC):
    """
    A listener on a Journal that receives notification of entries when they are added
    """
    def __init__(self):
        pass

    @abc.abstractmethod
    def is_interested(self, entry: Entry):
        """
        Pre-consume the entry and decides if this Consumer is interested in it by returning True. If it does not return interest (return True) then the consume method is never called
        """
        pass

    @abc.abstractmethod
    def consume(self, entry: Entry):
        """
        Consume the latest Journal entry
        """
        pass

class TextEntry(Entry):
    """
    Implements a basic Entry which includes just a String message
    """
    def __init__(self, text, entry_target: EntryTarget=EntryTarget.CONTENT, entry_type: EntryType=EntryType.NORMAL):
        self.__text = text
        super().__init__(entry_target, entry_type)
    
    def to_readable(self):
        return self.__text

    @property
    def text(self):
        return self.__text

class ParagraphBreakEntry(Entry):
    """
    Implements a basic Entry which indicates a break within a chapter
    """
    def __init__(self, entry_target: EntryTarget=EntryTarget.CONTENT, entry_type: EntryType=EntryType.NORMAL):
        super().__init__(entry_target, entry_type)
    
    def to_readable(self):
        return "--- Paragraph Break ---"

class OpenChapterEntry(Entry):
    """
    Entry automatically added by the Journal when a new chapter is opened
    """
    def __init__(self, name):
        if not name:
            raise ValueError('A name must be provided for the Chapter')
        self.__name = name
        super().__init__(EntryTarget.CONTENT, EntryType.NORMAL)

    def to_readable(self):
        return "Chapter: {0}".format(self.__name)

    @property
    def chapter_name(self):
        return self.__name

class CloseChapterEntry(Entry):
    """
    Entry automatically added by the Journal when chapter is closed
    """
    def __init__(self, name):
        if not name:
            raise ValueError('A name must be provided for the Chapter')
        self.__name = name
        super().__init__(EntryTarget.CONTENT, EntryType.NORMAL)

    def to_readable(self):
        return "End: {0}".format(self.__name)

    @property
    def chapter_name(self):
        return self.__name

class Journal:
    """
    The main entry class of the journal module. Represents the abstract concept of Journal, adding entries into sensible groupings known as chapters. 
    The Journal class actually does very little but manage the opening and closing of chapters, before handing off entries to consumers so they may decide what to do with them.

    At a basic level, the Journal class (along with a simple JournalKeeper consumer) can be used to maintain a log of events that occur in a system.
    """
    def __init__(self):
        self.__current_chapter = None
        self.__consumers = []

    def register_consumer(self, consumer: Consumer):
        """
        Add a new Consumer to the Journal. The consumer will receive the next entry added.
        """
        self.__consumers.append(consumer)

    def open_chapter(self, chapter_name):
        """
        Open a new chapter in the Journal. A OpenChapterEntry will be sent out to it's consumers. No entries can be added to a Journal until a chapter is opened
        """
        if self.__current_chapter is not None:
            self.close_chapter()
        self.__current_chapter = chapter_name
        self.add_entry(OpenChapterEntry(chapter_name))
    
    def close_chapter(self):
        """
        Close the current chapter. This prevents any further entries being added to the Journal until a new chapter is opened. A CloseChapterEntry will be sent out to it's consumers.
        """
        self.__ensure_chapter_open()
        self.add_entry(CloseChapterEntry(self.__current_chapter))
        self.__current_chapter = None

    @property
    def current_chapter(self):
        """
        Get the name of the chapter currently open. If there is no open chapter then a ValueError will be raised
        
        Returns:
          str: the name of the chapter currently open
        """
        self.__ensure_chapter_open()
        return self.__current_chapter

    def add_entry(self, entry: Entry):
        """
        Add a new Entry to the chapter currently open. If there is no open chapter then a ValueError will be raised
        """
        self.__ensure_chapter_open()
        self.__handoff_entry_to_consumers(entry)

    def add_text(self, msg: str, entry_target: EntryTarget=EntryTarget.CONTENT, entry_type: EntryType=EntryType.NORMAL):
        """
        Convenience method to add a new TextEntry to the chapter currently open. If there is no open chapter then a ValueError will be raised
        """
        self.add_entry(TextEntry(msg, entry_target, entry_type))

    def paragraph_break(self, entry_target: EntryTarget=EntryTarget.CONTENT, entry_type: EntryType=EntryType.NORMAL):
        self.add_entry(ParagraphBreakEntry(entry_target, entry_type))

    def __handoff_entry_to_consumers(self, entry):
        for consumer in self.__consumers:
            if consumer.is_interested(entry) == True:
                consumer.consume(entry)

    def __ensure_chapter_open(self):
        if self.__current_chapter is None:
            raise ValueError('No chapter started')

class JournalKeeper(Consumer):
    """
    A standard consumer implementation to keep hold of all the chapters and their entries (in memory)
    """
    def __init__(self):
        self.__chapters = []
        self.__current_chapter = None
        super().__init__()

    def is_interested(self, entry: Entry):
        return True

    def consume(self, entry: Entry):
        if isinstance(entry, OpenChapterEntry):
            self.__current_chapter = self.Chapter(entry.chapter_name)
            self.__chapters.append(self.__current_chapter)
        elif isinstance(entry, CloseChapterEntry):
            self.__current_chapter = None
        else:
            if self.__current_chapter:
                self.__current_chapter.entries.append(entry)

    @property
    def chapters(self):
        return self.__chapters

    class Chapter():
        def __init__(self, name):
            self.__name = name
            self.__entries = []

        @property
        def name(self):
            return self.__name

        @property
        def entries(self):
            return self.__entries


        
        

