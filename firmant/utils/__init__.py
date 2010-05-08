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


'''Utilities that don't fit anywhere else.

Modules in this package:

.. autosummary::
   :toctree: ../generated

   exceptions
   paths

'''


import datetime
import inspect
import os
import sys

from pysettings import modules


def class_name(cls):
    '''The string representation of a class's name.

    For example if we define the class `Foo`, the full name of the class
    is `firmant.utils.Foo`.  :func:`class_name` will return this as a string.

    .. doctest::

       >>> class Foo(object): pass
       ...
       >>> class_name(Foo)
       'firmant.utils.Foo'

    If an object that is not a class is passed to :func:`class_name`, then a
    :exc:`TypeError` will be raised.

    .. doctest::

       >>> class_name('Foo')
       Traceback (most recent call last):
       TypeError: `cls` does not name a type.

    '''
    if inspect.isclass(cls):
        return str(cls)[8:-2]
    else:
        raise TypeError('`cls` does not name a type.')


def strptime(date_string, formats):
    '''Cast the date_string to the first format to match.

    Each format string provided by `formats` is considered.  The first format to
    match `date_string` will be used to determine the datetime.

    .. doctest::

       >>> strptime('2009-02-01 11:51:15', ['%Y-%m-%d %H:%M:%S'])
       datetime.datetime(2009, 2, 1, 11, 51, 15)
       >>> strptime('11:51:15', ['%Y-%m-%d', '%H:%M:%S'])
       datetime.datetime(1900, 1, 1, 11, 51, 15)

    If the time does not match, a value error will be raised.

    .. doctest::

       >>> strptime('AB:CD:EF', ['%H:%M:%S'])
       Traceback (most recent call last):
       ValueError: time data 'AB:CD:EF' does not match any format.

    '''
    error = None
    dt    = None
    for frmt in formats:
        try:
            dt = dt or datetime.datetime.strptime(date_string, frmt)
        except ValueError:
            pass
    if dt is None:
        error = "time data '%s' does not match any format." % date_string
        raise ValueError(error)
    return dt


def merge_dicts(a, *args):
    '''Merge two dictionaries in a manner that doesn't lose information.

    One or two dictionaries with disjoint sets of keys will merge with the same
    rules as the :func:`update` function for dictionaries.

    .. doctest::

       >>> pprint(merge_dicts({'a': 1}))
       {'a': 1}
       >>> pprint(merge_dicts({'a': 1}, {'b': 2}))
       {'a': 1, 'b': 2}

    If two keys have the same value, the merge happens cleanly.

    .. doctest::

       >>> pprint(merge_dicts({'a': 1, 'b': 2}, {'b': 2}))
       {'a': 1, 'b': 2}

    An arbitrary number of dictionaries may be merged using :func:`merge_dicts`.

    .. doctest::

       >>> pprint(merge_dicts({'a': 1, 'b': 2}, {'b': 2}, {'c':3}))
       {'a': 1, 'b': 2, 'c': 3}

    If two instances have the same key, but different values, a
    :exc:`ValueError` will be raised.

    .. doctest::

       >>> pprint(merge_dicts({'a': 1, 'b': 2}, {'b': 3}))
       Traceback (most recent call last):
       ValueError: Conflicting values for 'b'

    '''
    ret = a.copy()
    for b in args:
        conflicts = set(a.keys()) & set(b.keys())
        for key in conflicts:
            if key in a and key in b and a[key] != b[key]:
                raise ValueError("Conflicting values for '%s'" % key)
        ret.update(b)
    return ret


def get_obj(path):
    '''Get an object by its Python import path.

    .. doctest::

       >>> get_obj('os.path.join') #doctest: +ELLIPSIS
       <function join at 0x...>

    '''
    mod, attr = path.rsplit('.', 1)
    mod = modules.get_module(mod)
    return getattr(mod, attr)
