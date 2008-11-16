import re


class RegexURLLink(object):
    '''
    A class used to declare a single bi-directional association between a URL
    regular expression and its callable function
    '''

    def __init__(self, urlregex, callable, kwargs=None):
        '''
        Create a new link between a regular expression for a URL and its
        callable function.  Both arguments should be strings.
        '''
        pass

    def rlookup(self, kwargs=None):
        '''
        Perform a reverse lookup.  That is, accept the kwargs and construct a
        URL using the kwargs to return to the user.
        '''
        pass

    def lookup(self, url):
        '''
        Perform a lookup.  That is, accept a URL and return a tuple with the
        callable and its kwargs.
        '''
        pass

    def add_prefix(self, prefix):
        '''
        Add the value to the beginning of the regular expression.  It should be
        a string literal.
        '''
        pass

    def parameters(self):
        '''
        Returns a set of the kwargs for the callable.  A set was chosen over
        other containers because it has no implicit order.
        '''


class URLHandler(object):
    '''
    This forms a list of RegexURLLinks and treats the list of a chain of
    responsibility.
    '''

    def handle(self, url):
        pass
