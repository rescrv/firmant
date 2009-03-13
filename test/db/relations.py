import unittest

from firmant.db import relations


class TestSchemaLoad(unittest.TestCase):

    def testLoad(self):
        self.assertEqual(relations.schema('loader-works'),
                         'SCHEMA LOAD WORKING PROPERLY')


class TestDB(unittest.TestCase):

    def testDBOmnipotent(self):
        conn = relations.DB.connection()
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

    class Dummy(relations.Relation):

        attributes = []

        def __init__(self):
            pass

    def testPermalink(self):
        self.assertRaises(RuntimeError, self.Dummy().permalink)

    def testInnerPermalink(self):
        self.assertRaises(RuntimeError, self.Dummy()._permalink)

    def testSet_permalink(self):
        f = lambda x: 'new'
        self.Dummy.set_permalink(f)
        self.assertEqual('new', self.Dummy().permalink())


suite = unittest.TestSuite()
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSchemaLoad))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDB))
suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestRelation))
