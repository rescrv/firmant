import re


class RegexURLLink(object):
    '''
    A class used to declare a single bi-directional association between a URL
    regular expression and its callable function
    '''

    def __init__(self, urlregex, callable, kwargs={}):
        '''
        Create a new link between a regular expression for a URL and its
        callable function.  Both arguments should be strings.
        '''
        self.url = re.compile(urlregex)
        module = '.'.join(callable.split('.')[:-1])
        attr = callable[len(module) + 1:]
        self.callable = getattr(__import__(module, {}, {}, ['']), attr)
        self.kwargs = kwargs

        # Check that url parameters + kwargs = callable's kwargs
        lhs = set(self.kwargs) | set(self.url.groupindex)
        rhs = self.parameters()
        if lhs != rhs:
            raise TypeError("Argument mismatch")

    def rlookup(self, kwargs=None):
        '''
        Perform a reverse lookup.  That is, accept the kwargs and construct a
        URL using the kwargs to return to the user.  It should raise a
        TypeError if the kwargs do not match.
        '''
        pass

    def lookup(self, url):
        '''
        Perform a lookup.  That is, accept a URL and return a tuple with the
        callable and its kwargs.  It should raise a TypeError if the URL does
        not match.
        '''
        results = self.url.match(url)
        if results is None:
            raise TypeError('URL Does Not Match')
        kwargs = self.kwargs
        kwargs.update(results.groupdict())
        return (self.callable, kwargs)

    def add_prefix(self, prefix):
        '''
        Add the value to the beginning of the regular expression.  It should be
        a string literal.
        '''
        url = self.url.pattern
        if url.startswith('^'):
            prefix = '^' + prefix
            url = url[1:]
        self.url = re.compile(prefix + url)

    def parameters(self):
        '''
        Returns a set of the kwargs for the callable.  A set was chosen over
        other containers because it has no implicit order.
        '''
        # This gets the variable names of the function the instance is
        # associated with.  It then removes the request function, as every
        # view function must have a request parameter.
        return set(self.callable.func_code.co_varnames) - set(['request'])

    def matches(self):
        '''
        Returns the regex string that is used for pattern matching.
        '''
        return self.url.pattern


class URLHandler(object):
    '''
    This forms a list of RegexURLLinks and treats the list of a chain of
    responsibility.
    '''

    def handle(self, url):
        pass
