import unittest

from firmant.db.relations import schema


class TestSchemaLoad(unittest.TestCase):

    def testLoad(self):
        if schema('loader-works') != 'SCHEMA LOAD WORKING PROPERLY':
            self.fail()

suite = unittest.TestLoader().loadTestsFromTestCase(TestSchemaLoad)
