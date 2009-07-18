import unittest

from firmant.filters import FilterProvider


def StaticFilter(replace):
    class Filter(object):

        def __init__(self, rc, settings):
            pass

        def filter(self, slot, contents):
            '''Changes all contents to replace'''
            return replace

        def provides(self, slot):
            return True
    return Filter


FooFilter = StaticFilter('foo')
BarFilter = StaticFilter('bar')


class FilterProviderTest(unittest.TestCase):

    def testFilterSingleProvider(self):
        '''firmant.filters.FilterProvider.filter
        Test the case that a single class provides the given slot.'''
        settings = {'TEXT_FILTERS': ['test.filters.FooFilter']}
        provider = FilterProvider(lambda: None, settings)

        expected = 'foo'
        returned = provider.filter('txt', 'Hello World!')

        self.assertEqual(expected, returned)

    def testFilterMultipleProviders(self):
        '''firmant.filters.FilterProvider.filter
        Test the case that multiple classes provide the given slot.'''
        settings = {'TEXT_FILTERS': ['test.filters.BarFilter',
                                     'test.filters.FooFilter']}
        provider = FilterProvider(lambda: None, settings)

        expected = 'bar'
        returned = provider.filter('txt', 'Hello World!')

        self.assertEqual(expected, returned)

    def testFilterNoProvider(self):
        '''firmant.filters.FilterProvider.filter
        Test the case that no class provides the given slot.'''
        settings = {'TEXT_FILTERS': []}
        provider = FilterProvider(lambda: None, settings)

        raises   = RuntimeError
        function = lambda: provider.filter('txt', 'Hello World!')

        self.assertRaises(raises, function)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, FilterProviderTest)
