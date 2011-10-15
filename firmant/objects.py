# Copyright (c) 2011, Robert Escriva
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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''Manage all objects, maintaining a mapping from keys to objects.

Objects are uniquely identified by a set of attributes represented as a
dictionary of Python strings.  These unique identifiers will be used with the
:mod:`firmant.urls` module to create permalinks for objects.
'''


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import collections


__all__ = ['add', 'retrieve']


_objs = {}


def add(key, obj):
    '''Add objects to the object store.

    Objects are added using key-value pairs.  The following example shows a blog
    post and a wiki object which are added.  All keys in the key dictionary must
    be unicode objects (this module imports unicode_literals from __future__).

    .. doctest::

       >>> add({'type': 'post', 'year': 2011, 'month': 10, 'day': 15, 'slug': 'hi'},
       ...     'blog object')
       ...
       True
       >>> add({'type': 'wiki', 'url': 'path/to/page'}, 'wiki object')
       True

    Two objects with the same key cannot exist.  Any attempt to add a duplicate
    object will fail.

    .. doctest::

       >>> add({'id': 'unique'}, 'a unique object')
       True
       >>> add({'id': 'unique'}, 'a different object')
       False

    '''
    key = tuple(sorted(key.items()))
    if key in _objs:
        return False
    _objs[key] = obj
    return True


def retrieve(key = None):
    '''Retrieve objects matching a pattern from the object store.

    Objects are retrieved by specifying the exact set of fields in the object's
    key.  The retrieval function takes exactly one argument which is a set or a
    dictionary of fields which define the object.  If a set is passed, all
    objects with the same fields will be returned.  If a dictionary is passed
    instead, the individual items in the dictionary will be matched.  A value of
    ``None`` for a field matches all objects, while a string value for the
    object retrieves only the objects which have the field which matches the
    value.

    .. doctest::

       >>> add({'field': 'a', 'otherfield': 'o'}, 'object')
       True
       >>> add({'field': 'a'}, 'object A')
       True
       >>> add({'field': 'b'}, 'object B')
       True
       >>> add({'field': 'c'}, 'object C')
       True
       >>> add({'field': 'd'}, 'object D')
       True
       >>> retrieve({'field'})
       [({u'field': u'a'}, u'object A'), ({u'field': u'b'}, u'object B'), ({u'field': u'c'}, u'object C'), ({u'field': u'd'}, u'object D')]
       >>> retrieve({'field': None})
       [({u'field': u'a'}, u'object A'), ({u'field': u'b'}, u'object B'), ({u'field': u'c'}, u'object C'), ({u'field': u'd'}, u'object D')]
       >>> retrieve({'field': 'a'})
       [({u'field': u'a'}, u'object A')]
       >>> retrieve({'otherfield': '0'})
       []

    '''
    key = key or {}
    filters = []
    for k in key:
        if isinstance(key, collections.Set):
            def filt(objkey, k=k):
                return k in objkey
            filters.append(filt)
        elif isinstance(key, collections.Mapping):
            v = key[k]
            def filt(objkey, k=k, v=v):
                return k in objkey and (v is None or objkey[k] == v)
            filters.append(filt)
    objs = [(dict(k), o) for k, o in sorted(_objs.items())]
    def matches(k):
        return all([f(k) for f in filters]) and all([i in key for i in k])
    return [(k, o) for k, o in objs if matches(k)]
