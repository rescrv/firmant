# Copyright (c) 2010, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Firmant nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


'''This module handles mapping between a set of attributes and a URL/document.

A :class:`URLMapper` serves as a means of converting a set of key-value pairs
into a full URL string.  Each instance of :class:`URLMapper` has a list of
objects that provide the :class:`AbstractPath` interface.  When querying
:meth:`URLMapper.url`, or :meth:`URLMapper.path`, the :class:`URLMapper` finds a
path object for which the provided attributes exactly cover the attributes of
the path.  Additionally, any bound variables must match the values provided in
the query.

.. note::

   Matching of attributes to URLs is designed to be similar to unification as
   found in Prolog, first order logic, and the lambda calculus; however, the
   similarity should not be read into too deeply as it may not be adhered to in
   the future.

Modules in this package:

.. autosummary::
   :toctree: ../generated

   components

'''


import abc
import os.path

from firmant.utils import class_name
from firmant.utils import merge_dicts
from firmant.utils import workarounds


__all__ = ['AbstractPath', 'BoundNullPathComponent', 'CompoundComponent',
        'SinglePathComponent', 'StaticPathComponent', 'URLMapper']


class AbstractPath(object):
    '''The interface for all path objects.

    The :class:`URLMapper` assumes all objects provided to it implement this
    interface.

    Intuitively, a path is simply a string that is defined by a set of
    key-value pairs.  The :attr:`attributes` property is the set of keys that
    define the path.

    The following properties must be true in any valid path object:

     * attributes = union(bound_attributes, free_attributes)
     * attributes - free_attributes = bound_attributes
     * attributes - bound_attributes = free_attributes

    '''

    __metaclass__ = abc.ABCMeta

    @workarounds.abstractproperty
    def attributes(self):
        '''All attributes that define the string representation of the path.
        '''

    @workarounds.abstractproperty
    def bound_attributes(self):
        '''Attributes with a fixed value.

        In order for a set of values to unify with this path, the keys and value
        of :attr:`bound_attributes` must match those specified in the query.

        '''

    @property
    def free_attributes(self):
        '''Attributes with no value.

        These attributes may be any value and still match the URL.

        '''
        return self.attributes - set(self.bound_attributes.keys())

    def match(self, *args, **kwargs):
        '''True if and only if `kwargs` and `args` specify the correct set of
        attributes.

        Each value in `args` should be a dictionary.  Provided keys must exactly
        cover all attributes and provided values must not conflict with bound
        attributes.  If the cover is not exact, or there are conflicting values,
        the result of :meth:`match` is False.

        '''
        # Do the merging of all values (if this throws a ValueError, we let it
        # rise because it is the fault of the caller).
        attrs = merge_dicts(kwargs, *args)

        # Check for conflict with bound values
        try:
            merge_dicts(attrs, self.bound_attributes)
        except ValueError:
            return False

        # Make sure the two sets are identical
        a = set(self.attributes)
        b = set(attrs.keys())
        return a & b == a | b

    @workarounds.abstractmethod
    def construct(self, *args, **kwargs):
        '''Use the values given in `kwargs` to construct the string
        representation of the path.

        The values in kwargs are not required to be any type, but should be of a
        type the path may safely convert to a string.

        '''

    def __div__(self, rhs):
        '''Concatenate two components (using :class:`CompoundComponent`).
        '''
        return CompoundComponent(self, rhs)


class SinglePathComponent(AbstractPath):
    '''A mapper between a single attribute and its string representation.

    Each instance will match exactly one attribute.  At creation time, a
    conversion function `conv` is specified that will be called to obtain the
    string representation of the attribute.

    In this example, a component with the attribute `month` is created.  When
    the :meth:`construct` method is called, it returns a two-digit
    representation of the number.

    .. doctest::

       >>> spc = SinglePathComponent('month', lambda m: '%02i' % m)
       >>> spc.attributes
       set(['month'])
       >>> spc.bound_attributes
       {}
       >>> spc.free_attributes
       set(['month'])
       >>> spc.match({'month': 3})
       True
       >>> spc.match(month=3)
       True
       >>> spc.match(year=2010)
       False
       >>> spc.match(year=2010, month=3)
       False
       >>> spc.construct({'month': 3})
       '03'
       >>> spc.construct(month=3)
       '03'

    It is an error to provide the same attribute twice with two different
    values:

    .. doctest::

       >>> spc.match({'month': 2}, month=3)
       Traceback (most recent call last):
       ValueError: Conflicting values for 'month'

    Note that the same attribute can be specified multiple times if the values
    are equal:

    .. doctest::

       >>> spc.match({'month': 3}, month=3)
       True

    If attributes not matching the single attribute are specified, then a
    :exc:`ValueError` will be thrown.

    .. doctest::

       >>> spc.construct(month=3, year=10)
       Traceback (most recent call last):
       ValueError: Attributes do not match path
       >>> spc.construct(year=10)
       Traceback (most recent call last):
       ValueError: Attributes do not match path
       >>> spc.construct()
       Traceback (most recent call last):
       ValueError: Attributes do not match path

    '''

    def __init__(self, attribute, conv=lambda x:x):
        super(SinglePathComponent, self).__init__()
        self._attribute = attribute
        self._conv = conv

    @property
    def attributes(self):
        '''The set of attributes contains the single attribute specified at
        creation time.
        '''
        return set([self._attribute])

    @property
    def bound_attributes(self):
        '''No attributes are bound.  This will always be an empty dictionary.
        '''
        return dict()

    def construct(self, *args, **kwargs):
        '''Create the string representation of the path.

        The value of the attribute will be passed through the conversion
        function.  The conversion function may return `None`.

        '''
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match path')
        attr = merge_dicts(kwargs, *args)
        return self._conv(attr[self._attribute])


class BoundNullPathComponent(AbstractPath):
    '''A mapper between a single attribute and the empty string.

    Each instance will match exactly one attribute.  Construct will always
    return `None` if there is a match.

    .. doctest::

       >>> bnpc = BoundNullPathComponent('month', 3)
       >>> bnpc.attributes
       set(['month'])
       >>> bnpc.bound_attributes
       {'month': 3}
       >>> bnpc.free_attributes
       set([])
       >>> bnpc.match({'month': 3})
       True
       >>> bnpc.match(month=3)
       True
       >>> bnpc.construct({'month': 3}) is None
       True
       >>> bnpc.construct(month=3) is None
       True

    It is an error to provide the same attribute twice with two different
    values:

    .. doctest::

       >>> bnpc.match({'month': 2}, month=3)
       Traceback (most recent call last):
       ValueError: Conflicting values for 'month'

    Note that the same attribute can be specified multiple times if the values
    are equal:

    .. doctest::

       >>> bnpc.match({'month': 3}, month=3)
       True

    If attributes not matching the single attribute are specified, then a
    :exc:`ValueError` will be thrown.

    .. doctest::

       >>> bnpc.construct(month=3, year=10)
       Traceback (most recent call last):
       ValueError: Attributes do not match path
       >>> bnpc.construct(year=10)
       Traceback (most recent call last):
       ValueError: Attributes do not match path
       >>> bnpc.construct()
       Traceback (most recent call last):
       ValueError: Attributes do not match path

    '''

    def __init__(self, attribute, value):
        super(BoundNullPathComponent, self).__init__()
        self._attribute = attribute
        self._value = value

    @property
    def attributes(self):
        '''The set of attributes contains the single attribute specified at
        creation time.

        '''
        return set([self._attribute])

    @property
    def bound_attributes(self):
        '''The single attribute is bound to the value specified.
        '''
        attrs = dict()
        attrs[self._attribute] = self._value
        return attrs

    def construct(self, *args, **kwargs):
        '''This will return `None` if the attributes match, or raise a
        :exc:`ValueError` otherwise.
        '''
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match path')
        return None


class StaticPathComponent(AbstractPath):
    '''A path component with no attributes that creates a static string.

    In this example, a path component is created that will construct to the path
    ``images``:

    .. doctest::

       >>> spc = StaticPathComponent('images')
       >>> spc.attributes
       set([])
       >>> spc.bound_attributes
       {}
       >>> spc.free_attributes
       set([])
       >>> spc.match({'month': 3})
       False
       >>> spc.match()
       True
       >>> spc.construct()
       'images'

    It is an error to specify any attributes when constructing:

    .. doctest::

       >>> spc.construct(month=2)
       Traceback (most recent call last):
       ValueError: Do not specify attributes for StaticPathComponent

    '''

    def __init__(self, path):
        super(StaticPathComponent, self).__init__()
        self._path = str(path)

    @property
    def attributes(self):
        '''By definition, a :class:`StaticPathComponent` has no attributes.

        This will return the empty set.

        '''
        return set([])

    @property
    def bound_attributes(self):
        '''By definition, a :class:`StaticPathComponent` has no attributes.

        This will return an empty dictionary.

        '''
        return {}

    def construct(self, *args, **kwargs):
        '''The constructed path is always the string constant specified.
        '''
        if not self.match(*args, **kwargs):
            raise ValueError(
                    'Do not specify attributes for StaticPathComponent')
        return self._path


class CompoundComponent(AbstractPath):
    '''A path object formed by joining two or more path objects with '/'.

    A :class:`CompoundComponent` is transparently formed by dividing path
    objects.

    .. doctest::

       >>> tags = StaticPathComponent('tags')
       >>> type = BoundNullPathComponent('type', 'tag')
       >>> slug = SinglePathComponent('slug', str)
       >>> path = type/tags/slug
       >>> path #doctest: +ELLIPSIS
       <firmant.routing.CompoundComponent object at 0x...>
       >>> path.match(type='tag', slug='foobar')
       True
       >>> path.match(type='tag')
       False
       >>> path.match(slug='foobar')
       False
       >>> path.construct(type='tag', slug='foobar')
       'tags/foobar'

    If :meth:`construct` is called with attributes that do not match the path,
    then a :exc:`ValueError` will be thrown.

    .. doctest::

       >>> path.construct(type='tag')
       Traceback (most recent call last):
       ValueError: Attributes do not match path

    '''

    def __init__(self, *args):
        super(CompoundComponent, self).__init__()
        self._components = args
        bound_attributes = [c.bound_attributes for c in self._components]
        self._bound = merge_dicts({}, *bound_attributes)

    @property
    def attributes(self):
        '''The attributes are the union of all components' attributes.
        '''
        return reduce(set.__or__, [c.attributes for c in self._components])

    @property
    def bound_attributes(self):
        '''The attributes are the union of all components' bound_attributes.
        '''
        return self._bound

    def construct(self, *args, **kwargs):
        '''Construct each path component, and join with '/'.
        '''
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match path')
        bound = merge_dicts(kwargs, *args)
        list_of_paths = [self._construct(x, bound) for x in self._components]
        list_of_paths = [p for p in list_of_paths if p]
        return '/'.join(list_of_paths)

    @classmethod
    def _construct(cls, component, d):
        '''A utility function for construct.

        Keys in `d` that are not in `component.attributes` are discarded before
        calling `component.construct`.

        '''
        d = d.copy()
        for key in d.keys():
            if key not in component.attributes:
                d.pop(key, None)
        return component.construct(d)


class URLMapper(object):
    '''Find the url or filesystem path that correlate with a set of attributes.

    The distinction between urls and paths is best described by example.  Let's
    declare the attributes ``slug='foo'`` and ``type='object'``.  The path on
    the filesystem, where the output would be written could be
    ``/path/to/output/directory/objects/foo/index.html`` while the URL where the
    document is accessible would be ``http://permanent.url/objects/foo/``.

    Having the URLMapper handle the logic of both paths and URLs makes sense.
    Consider a case where the user wishes to have the above URL be
    ``http://permanent.url/objects/foo.html``.  The local filesystem path
    would need to adapt to ``/path/to/output/directory/objects/foo.html``

    Creating a URLMapper is simple:

    .. doctest::

       >>> from firmant.routing.components import *
       >>> um = URLMapper('/path/to/output/directory', 'http://permanent.url/')
       >>> um.add( TYPE('post')/YEAR/MONTH/DAY/SLUG )
       >>> um.add( TYPE('post')/YEAR/MONTH/DAY )
       >>> um.add( TYPE('post')/YEAR/MONTH )
       >>> um.add( TYPE('post')/YEAR )

    Mapping a set of attributes to a path or URL is a matter of specifying the
    extension of the document (e.g. 'html' or 'css') and a set of key-value
    attributes.

    .. doctest::

       >>> um.path('html', type='post', slug='foo', day=15, month=3, year=2010)
       '/path/to/output/directory/2010/03/15/foo/index.html'
       >>> um.url('html', type='post', slug='foo', day=15, month=3, year=2010)
       'http://permanent.url/2010/03/15/foo/'

    .. todo::

       Add tests (and support) for multiple extensions for the same set of
       attributes.

    If the attributes do not correspond to any path definition, then the value
    `None` is returned:

    .. doctest::

       >>> um.path('html', non_existent_attribute=True)
       >>> um.url('html', non_existent_attribute=True)

    If the extension is `None`, then the :meth:`path` and :meth:`url` methods
    will not add any information to account for an extension.

    .. doctest::

       >>> um.path(None, type='post', slug='foo', day=15, month=3, year=2010)
       '/path/to/output/directory/2010/03/15/foo'
       >>> um.url(None, type='post', slug='foo', day=15, month=3, year=2010)
       'http://permanent.url/2010/03/15/foo'

    This is useful when it is known that the attributes specified promise to
    resolve to a path.  Example uses include static files that are simply copied
    into the output directory.

    '''

    def __init__(self, output_dir, url_root, urls=None):
        self.output_dir = output_dir
        self.url_root   = url_root

        self._paths = list()
        if urls is not None:
            self._paths.extend(urls)

    def add(self, path):
        '''Add the path to the list of paths in the :class:`URLMapper`
        '''
        self._paths.append(path)

    def __lookup__(self, **kwargs):
        for path in self._paths:
            if path.match(kwargs):
                return path.construct(kwargs)
        raise AttributeError('Attributes do not correspond to any path')

    def url(self, extension, **kwargs):
        '''Return the URL corresponding to a set of attributes.
        '''
        try:
            path = self.__lookup__(**kwargs)
        except AttributeError:
            return None
        path = os.path.join(self.url_root, path or '')
        if extension is not None and not path.endswith('/'):
            path += '/'
        return path

    def path(self, extension, **kwargs):
        '''Return the filesystem path corresponding to a set of attributes.
        '''
        try:
            path = self.__lookup__(**kwargs)
        except AttributeError:
            return None
        path = os.path.join(self.output_dir, path or '')
        if extension is not None:
            path = os.path.join(path, 'index.%s' % extension)
        return path
