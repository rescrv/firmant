import unittest

from firmant.configuration import settings
from firmant.plugins.datasource.flatfile.atom import Entry
from test.datasource.atom import generate_e1, \
                              generate_e2, \
                              generate_e3, \
                              generate_e4
from test.datasource.atom import TestEntry as BaseTestEntry


class TestEntry(BaseTestEntry):

    def setUp(self):
        self.Entry = Entry
        self.e1 = generate_e1(Entry)
        self.e2 = generate_e2(Entry)
        self.e3 = generate_e3(Entry)
        self.e4 = generate_e4(Entry)

    def tearDown(self):
        pass

    def loadData(self):
        pass


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEntry))
