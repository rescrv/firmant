import unittest
import psycopg2
from firmant.configuration import settings
import os

from firmant.db import relations


class DB(object):

    @staticmethod
    def connection(readonly=True):
        return psycopg2.connect(settings['OMNIPOTENT_DB_CONNECT'])


def schema(schema_name):
    '''
    This function takes a string argument such as 'atom' and loads the
    corresponding file firmant/db/schemas/<name>.sql and returns the file as
    text.
    '''
    mod = __import__('firmant.db.schemas', {}, {}, ['schemas'])
    schema = os.path.join(os.path.dirname(mod.__file__), schema_name + '.sql')
    del mod
    f = open(schema)
    schema = f.read()
    f.close()
    del f
    return schema


class TestSchemaLoad(unittest.TestCase):

    def testLoad(self):
        self.assertEqual(schema('loader-works'),
                         'SCHEMA LOAD WORKING PROPERLY')


class TestDB(unittest.TestCase):

    def testDBOmnipotent(self):
        conn = DB.connection()
        conn.close()


class TestRelation(unittest.TestCase):

    class ExampleRelation(relations.Relation):

        attributes = ['foo']

    class FakeCursor(object):

        def fetchone(self):
            return ('foo', 'bar')

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

    def testEqualComparison(self):
        e1 = self.ExampleRelation()
        e2 = self.ExampleRelation()
        self.assertEqual(e1, e2)

        e1.foo = 'foobar'
        e2.foo = 'foobar'
        self.assertEqual(e1, e2)

    def testNotEqualComparison(self):
        e1 = self.ExampleRelation()
        e2 = self.ExampleRelation()
        e1.foo = 'foobar'
        e2.foo = 'barfoo'
        # We use this convoluted means instead of assertNotEqual as this means
        # calls __ne__ while assertNotEqual really calls __eq__.
        self.assertEqual(e1 != e2, True)


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSchemaLoad))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDB))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRelation))
