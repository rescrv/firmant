import unittest

from firmant.db.relations import schema


class TestSchemaLoad(unittest.TestCase):

    def testLoad(self):
        self.assertEqual(schema('loader-works'), 'SCHEMA LOAD WORKING PROPERLY')

suite = unittest.TestLoader().loadTestsFromTestCase(TestSchemaLoad)
