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


'''This module handles mapping between paths and writers.

Writers are able to request a URL for a given set of attributes.
'''


import os.path

from firmant.utils import class_name
from firmant.utils import merge_dicts


class AbstractPath(object):
    '''The path component of a URL.

    This may be a single component, several components, or a whole URL.

    Intentionally the following methods and attributes raise errors indicating
    that they have not been implemented::

        >>> ap = AbstractPath()
        >>> ap.attributes
        Traceback (most recent call last):
        RuntimeError: Not Implemented
        >>> ap.bound_attributes
        Traceback (most recent call last):
        RuntimeError: Not Implemented
        >>> ap.construct()
        Traceback (most recent call last):
        RuntimeError: Not Implemented

    '''

    @property
    def attributes(self):
        raise RuntimeError("Not Implemented")

    @property
    def bound_attributes(self):
        raise RuntimeError("Not Implemented")

    @property
    def free_attributes(self):
        return self.attributes - set(self.bound_attributes.keys())

    def match(self, *args, **kwargs):
        # Provided values must exactly cover all attributes and not conflict
        # with bound attributes.
        d = merge_dicts(kwargs, *args)

        # Check for conflict with bound values
        try:
            merge_dicts(d, self.bound_attributes)
        except ValueError:
            return False

        a = set(self.attributes)
        b = set(d.keys())
        return a & b == a | b

    def construct(self, *args, **kwargs):
        raise RuntimeError("Not Implemented")

    def __div__(self, rhs):
        return CompoundComponent(self, rhs)


class SinglePathComponent(AbstractPath):
    '''A single piece of a URL.

    Example usage::

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

    Error conditions::

        >>> spc.match({'month': 2}, month=3)
        Traceback (most recent call last):
        ValueError: Conflicting values for 'month'
        >>> spc.construct(month=3, year=10)
        Traceback (most recent call last):
        ValueError: Attributes do not match URL

    '''

    def __init__(self, attribute, conv=lambda x:x):
        self._attribute = attribute
        self._conv = conv

    @property
    def attributes(self):
        return set([self._attribute])

    @property
    def bound_attributes(self):
        return dict()

    def construct(self, *args, **kwargs):
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match URL')
        d = merge_dicts(kwargs, *args)
        return self._conv(d[self._attribute])


class BoundNullPathComponent(AbstractPath):
    '''A path component that does not impact the URL.

    In this example, a path component is created that will match if the
    attribute `month` is 3::

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

    '''

    def __init__(self, attribute, value):
        self._attribute = attribute
        self._value = value

    @property
    def attributes(self):
        return set([self._attribute])

    @property
    def bound_attributes(self):
        d = dict()
        d[self._attribute] = self._value
        return d

    def construct(self, *args, **kwargs):
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match URL')
        return None


class StaticPathComponent(AbstractPath):
    '''A path component that does not have any attributes.

    In this example, a path component is created that will construct to the path
    ``images``::

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

    '''

    def __init__(self, path):
        self._path = str(path)

    @property
    def attributes(self):
        return set([])

    @property
    def bound_attributes(self):
        return {}

    def construct(self, *args, **kwargs):
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match URL')
        return self._path


class CompoundComponent(AbstractPath):
    '''A compound path formed using zero or more AbstractPath objects.

    Example usage::

        >>> year = SinglePathComponent('year', lambda y: '%04i' % y)
        >>> month = SinglePathComponent('month', lambda m: '%02i' % m)
        >>> day = SinglePathComponent('day', lambda d: '%02i' % d)
        >>> ymd = year/month/day
        >>> ymd #doctest: +ELLIPSIS
        <firmant.routing.CompoundComponent object at 0x...>
        >>> ymd.match(year=2010, month=3, day=14)
        True
        >>> ymd.match(year=2010, month=3, day=14, slug='foobar')
        False
        >>> ymd.construct(year=2010, month=3, day=14)
        '2010/03/14'

    With a null path component::

        >>> bnpc = BoundNullPathComponent('type', 'tag')
        >>> slug = SinglePathComponent('slug', str)
        >>> path = bnpc/slug
        >>> path #doctest: +ELLIPSIS
        <firmant.routing.CompoundComponent object at 0x...>
        >>> path.attributes
        set(['type', 'slug'])
        >>> path.bound_attributes
        {'type': 'tag'}
        >>> path.free_attributes
        set(['slug'])
        >>> path.match(slug='foobar')
        False
        >>> path.match(type='tag', slug='foobar')
        True
        >>> path.construct(type='tag', slug='foobar')
        'foobar'

    With a static path component::

        >>> spc = StaticPathComponent('images')
        >>> slug = SinglePathComponent('slug', str)
        >>> path = spc/slug
        >>> path #doctest: +ELLIPSIS
        <firmant.routing.CompoundComponent object at 0x...>
        >>> path.attributes
        set(['slug'])
        >>> path.bound_attributes
        {}
        >>> path.free_attributes
        set(['slug'])
        >>> path.match(slug='foobar')
        True
        >>> path.match(type='tag', slug='foobar')
        False
        >>> path.construct(slug='foobar')
        'images/foobar'

    '''

    def __init__(self, *args):
        self._components = args

    @property
    def attributes(self):
        list_of_sets = map(lambda x: x.attributes, self._components)
        return reduce(set.__or__, list_of_sets)

    @property
    def bound_attributes(self):
        list_of_sets = map(lambda x: x.bound_attributes, self._components)
        return reduce(merge_dicts, list_of_sets)

    def construct(self, *args, **kwargs):
        if not self.match(*args, **kwargs):
            raise ValueError('Attributes do not match URL')
        d = merge_dicts(kwargs, *args)
        list_of_paths = map(lambda x: self._call_construct(x, d),
                self._components)
        list_of_paths = filter(bool, list_of_paths)
        return '/'.join(list_of_paths)

    @classmethod
    def _call_construct(cls, component, d):
        e = d.copy()
        for key in e.keys():
            if key not in component.attributes:
                e.pop(key, None)
        return component.construct(e)


class URLMapper(object):
    '''Convert between attributes and paths.

    Example::

        >>> # setup (this would be done by the Firmant object)
        >>> post = BoundNullPathComponent('type', 'post')
        >>> year = SinglePathComponent('year', lambda y: '%04i' % y)
        >>> month = SinglePathComponent('month', lambda m: '%02i' % m)
        >>> day = SinglePathComponent('day', lambda d: '%02i' % d)
        >>> slug = SinglePathComponent('slug', str)
        >>> from pysettings.settings import Settings
        >>> um = URLMapper(root='http://test')
        >>> um.add( post/year/month/day/slug )
        >>> um.add( post/year/month/day )
        >>> um.add( post/year/month )
        >>> um.add( post/year )

        >>> # usage (this would be done within writers/transformers)
        >>> um.lookup(type='post', slug='foobar', day=15, month=3, year=2010)
        '2010/03/15/foobar'
        >>> um.lookup(type='post', year=2010)
        '2010'
        >>> um.lookup(type='post', unknown_attribute=True)
        Traceback (most recent call last):
        AttributeError: Attributes do not correspond to any path
        >>> um.urlfor('html', type='post', slug='foobar', day=15, month=3, year=2010)
        '2010/03/15/foobar/index.html'
        >>> um.urlfor('html', type='post', year=2010)
        '2010/index.html'
        >>> um.urlfor('html', type='post', unknown_attribute=True) is None
        True

    If `absolute` is True, the URL will be prefixed with the root (if it was
    specified).

        >>> um.urlfor('html', type='post', absolute=True, slug='foobar', day=15, month=3, year=2010)
        'http://test/2010/03/15/foobar/index.html'

    If `format` is '', then the path formed by the attributes is kept as is and is
    not interpreted as a directory with an 'index.%s' % format path appended::

        >>> um.urlfor('', type='post', absolute=True, slug='foobar', day=15, month=3, year=2010)
        'http://test/2010/03/15/foobar'

    '''

    def __init__(self, urls=None, root=None):
        self.root=root
        self._paths = list()
        if urls is not None:
            self._paths.extend(urls)

    def add(self, path):
        self._paths.append(path)

    def lookup(self, **kwargs):
        '''Lookup the abstract representation of a page defined by attributes.

        Unless you know to do otherwise, use :method:`urlfor` instead of this
        method.
        '''
        for path in self._paths:
            if path.match(kwargs):
                return path.construct(kwargs)
        raise AttributeError('Attributes do not correspond to any path')

    def urlfor(self, format, absolute=False, **kwargs):
        '''Return the path of a page relative to the content root.

        Unless you know to do otherwise, use this method instead of
        :method:`lookup`.

        '''
        try:
            path = self.lookup(**kwargs)
        except AttributeError:
            return None
        path = path or ''
        if absolute and self.root is None:
            raise RuntimeError('Set the root for absolute URLs')
        if format != '':
            path = os.path.join(path, 'index.%s' % format)
        if absolute:
            return self.absolute(path)
        else:
            return path

    def absolute(self, path):
        '''Return the absolute url for the path.
        '''
        return os.path.join(self.root, path)
