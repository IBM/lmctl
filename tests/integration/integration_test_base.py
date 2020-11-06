import tempfile
import os
import shutil
import unittest
from .integration_tester import IntegrationTester

class IntegrationTest(unittest.TestCase):
    tester: IntegrationTester = None
    test_id: int = 1

    @classmethod
    def setUpClass(cls):
        if IntegrationTest.tester is None:
            IntegrationTest.tester = IntegrationTester()
        IntegrationTest.tester.start()
        cls.before_test_case(IntegrationTest.tester)

    @classmethod
    def tearDownClass(cls):
        cls.after_test_case(IntegrationTest.tester)
        IntegrationTest.tester.close()

    @classmethod
    def before_test_case(cls, tester):
        pass

    @classmethod
    def after_test_case(cls, tester):
        pass

    def setUp(self):
        self.local_tmp_dir = tempfile.mkdtemp(prefix='lmctl_tests')
        IntegrationTest.tester.test_id += 1
        self.before_test()

    def tearDown(self):
        self.after_test()
        if os.path.exists(self.local_tmp_dir):
            shutil.rmtree(self.local_tmp_dir)

    def before_test(self):
        pass

    def after_test(self):
        pass

