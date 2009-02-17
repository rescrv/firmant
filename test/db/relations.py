import unittest

from firmant.db import relations


class TestSchemaLoad(unittest.TestCase):

    def testLoad(self):
        self.assertEqual(relations.schema('loader-works'), 'SCHEMA LOAD WORKING PROPERLY')


class TestDB(unittest.TestCase):

    def testDBOmnipotent(self):
        conn = relations.DB.connection()
        conn.close()


class TestRelation(unittest.TestCase):

    class ExampleRelation(relations.Relation):

        attributes = ['foo']

    class FakeCursor(object):

        def fetchone(self):
            return ('foo', 'bar',)

        def close(self):
            pass

    def testNonInstantiable(self):
        self.assertRaises(NotImplementedError, relations.Relation)

    def testAttributeCheck(self):
        self.assertRaises(AttributeError, self.ExampleRelation._select,
                                          None, ['bar'])

    def testQueryCheck(self):
        self.assertRaises(ValueError, self.ExampleRelation._select,
                                      self.FakeCursor(), ['foo'])


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSchemaLoad))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDB))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRelation))
