import unittest
from lmctl.journal import *

class TestEntryTarget(unittest.TestCase):

    def test_order(self):
        self.assertGreater(EntryTarget.CONTENT.value, EntryTarget.SIDENOTE.value)
        self.assertGreater(EntryTarget.SIDENOTE.value, EntryTarget.FOOTNOTE.value)

class TestTextEntry(unittest.TestCase):

    def test_defaults(self):
        text_entry = TextEntry("test entry")
        self.assertEqual(text_entry.entry_target, EntryTarget.CONTENT)
        self.assertEqual(text_entry.entry_type, EntryType.NORMAL)

    def test_set_entry_and_format(self):
        text_entry = TextEntry("test entry", EntryTarget.SIDENOTE, EntryType.WARNING)
        self.assertEqual(text_entry.entry_target, EntryTarget.SIDENOTE)
        self.assertEqual(text_entry.entry_type, EntryType.WARNING)

    def test_readable(self):
        text_entry = TextEntry("test entry")
        self.assertEqual(text_entry.to_readable(), "test entry")

class TestOpenChapterEntry(unittest.TestCase):

    def test_no_name(self):
        with self.assertRaises(ValueError) as context:
            entry = OpenChapterEntry(None)
        self.assertTrue('A name must be provided for the Chapter' in str(context.exception))        
        
    def test_properties(self):
        entry = OpenChapterEntry("TestChapter")
        self.assertEqual(entry.chapter_name, "TestChapter")
        self.assertEqual(entry.entry_type, EntryType.NORMAL)
        self.assertEqual(entry.entry_target, EntryTarget.CONTENT)

    def test_readable(self):
        entry = OpenChapterEntry("TestChapter")
        self.assertEqual(entry.to_readable(), "Chapter: TestChapter")

class TestCloseChapterEntry(unittest.TestCase):

    def test_no_name(self):
        with self.assertRaises(ValueError) as context:
            entry = CloseChapterEntry(None)
        self.assertTrue('A name must be provided for the Chapter' in str(context.exception))        
        
    def test_properties(self):
        entry = CloseChapterEntry("TestChapter")
        self.assertEqual(entry.chapter_name, "TestChapter")
        self.assertEqual(entry.entry_type, EntryType.NORMAL)
        self.assertEqual(entry.entry_target, EntryTarget.CONTENT)

    def test_readable(self):
        entry = CloseChapterEntry("TestChapter")
        self.assertEqual(entry.to_readable(), "End: TestChapter")

class PlainJournalConsumer(Consumer):

    def __init__(self):
        self.entries = []
        super().__init__()

    def is_interested(self, entry: Entry):
        return True

    def consume(self, entry: Entry):
        self.entries.append(entry)

class TestJournal(unittest.TestCase):

    def test_open_chapter(self):
        journal = Journal()
        consumer = PlainJournalConsumer()
        journal.register_consumer(consumer)
        journal.open_chapter("Test")

        self.assertEqual(len(consumer.entries), 1)
        self.assertIsInstance(consumer.entries[0], OpenChapterEntry)
        self.assertEqual(consumer.entries[0].chapter_name, "Test")

    def test_close_chapter(self):
        journal = Journal()
        consumer = PlainJournalConsumer()
        journal.register_consumer(consumer)
        journal.open_chapter("Test")
        journal.close_chapter()
        self.assertEqual(len(consumer.entries), 2)
        self.assertIsInstance(consumer.entries[1], CloseChapterEntry)
        self.assertEqual(consumer.entries[1].chapter_name, "Test")

    def test_close_chapter_not_started(self):
        journal = Journal()
        with self.assertRaises(ValueError) as context:
            journal.close_chapter()
        self.assertTrue('No chapter started' in str(context.exception))       

    def test_add_text_no_chapter_started(self):
        journal = Journal()
        with self.assertRaises(ValueError) as context:
            journal.add_text("Test Entry")
        self.assertTrue('No chapter started' in str(context.exception))        

    def test_add_entry_no_chapter_started(self):
        journal = Journal()
        with self.assertRaises(ValueError) as context:
            journal.add_entry(TextEntry("Test Entry"))
        self.assertTrue('No chapter started' in str(context.exception))        

    def test_add_text(self):
        journal = Journal()
        consumer = PlainJournalConsumer()
        journal.register_consumer(consumer)
        journal.open_chapter("Test")
        journal.add_text("Test Entry")
        self.assertEqual(len(consumer.entries), 2)
        self.assertIsInstance(consumer.entries[1], TextEntry)
        self.assertEqual(consumer.entries[1].to_readable(), "Test Entry")

    def test_add_entry(self):
        journal = Journal()
        consumer = PlainJournalConsumer()
        journal.register_consumer(consumer)
        journal.open_chapter("Test")
        journal.add_entry(TextEntry("Test Entry"))
        self.assertEqual(len(consumer.entries), 2)
        self.assertIsInstance(consumer.entries[1], TextEntry)
        self.assertEqual(consumer.entries[1].to_readable(), "Test Entry")

    def test_add_paragraph_break(self):
        journal = Journal()
        consumer = PlainJournalConsumer()
        journal.register_consumer(consumer)
        journal.open_chapter("Test")
        journal.paragraph_break()
        self.assertEqual(len(consumer.entries), 2)
        self.assertIsInstance(consumer.entries[1], ParagraphBreakEntry)

    def test_no_consumers(self):
        journal = Journal()
        journal.open_chapter("Test")
        journal.add_text("Test Entry")

    def test_multiple_consumers(self):
        journal = Journal()
        consumer1 = PlainJournalConsumer()
        consumer2 = PlainJournalConsumer()
        journal.register_consumer(consumer1)
        journal.register_consumer(consumer2)
        journal.open_chapter("Test")
        journal.add_text("Test Entry")
        journal.close_chapter()
        self.assertEqual(len(consumer1.entries), 3)
        self.assertEqual(len(consumer2.entries), 3)

class TestJournalKeeper(unittest.TestCase):

    def test_is_interested(self):
        keeper = JournalKeeper()
        self.assertTrue(keeper.is_interested(OpenChapterEntry("Test")))
        self.assertTrue(keeper.is_interested(TextEntry("Test")))
        self.assertTrue(keeper.is_interested(CloseChapterEntry("Test")))
    
    def test_keep_chapters(self):
        keeper = JournalKeeper()
        keeper.consume(OpenChapterEntry("Test"))
        keeper.consume(CloseChapterEntry("Test"))
        keeper.consume(OpenChapterEntry("Test2"))
        
        self.assertEqual(len(keeper.chapters), 2)
        self.assertEqual(keeper.chapters[0].name, "Test")
        self.assertEqual(keeper.chapters[1].name, "Test2")

    def test_keep_entries(self):
        keeper = JournalKeeper()
        keeper.consume(OpenChapterEntry("Chapter1"))
        keeper.consume(TextEntry("Entry1"))
        keeper.consume(TextEntry("Entry2"))
        keeper.consume(CloseChapterEntry("Chapter1"))
        keeper.consume(OpenChapterEntry("Chapter2"))
        keeper.consume(TextEntry("Entry3"))
        keeper.consume(CloseChapterEntry("Chapter2"))

        self.assertEqual(len(keeper.chapters), 2)
        self.assertEqual(len(keeper.chapters[0].entries), 2)
        self.assertEqual(keeper.chapters[0].entries[0].to_readable(), "Entry1")
        self.assertEqual(keeper.chapters[0].entries[1].to_readable(), "Entry2")
        self.assertEqual(len(keeper.chapters[1].entries), 1)
        self.assertEqual(keeper.chapters[1].entries[0].to_readable(), "Entry3")