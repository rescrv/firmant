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


import datetime
import os
import sys


def class_name(cls):
    '''Return a string representation of a class's name.

        >>> class Foo(object): pass
        ...
        >>> class_name(Foo)
        'firmant.utils.Foo'

    '''
    return str(cls)[8:-2]


def strptime(date_string, formats):
    '''Cast the date_string to the first format to match.

    Examples::

        >>> strptime('2009-02-01 11:51:15', ['%Y-%m-%d %H:%M:%S'])
        datetime.datetime(2009, 2, 1, 11, 51, 15)
        >>> strptime('11:51:15', ['%H:%M:%S'])
        datetime.datetime(1900, 1, 1, 11, 51, 15)

    If the time does not match, a value error will be raised::

        >>> strptime('AB:CD:EF', ['%H:%M:%S'])
        Traceback (most recent call last):
        ValueError: time data 'AB:CD:EF' does not match any format.

    '''
    error = None
    dt    = None
    for format in formats:
        try:
            dt = dt or datetime.datetime.strptime(date_string, format)
        except ValueError:
            pass
    if dt is None:
        error = "time data '%s' does not match any format." % date_string
        raise ValueError(error)
    return dt


def merge_dicts(a, *args):
    '''Merge two dictionaries.  Return the merge.

    Where identical keys correspond to conflicting values, a ValueError is
    rasied.

        >>> pprint(merge_dicts({'a': 1}))
        {'a': 1}
        >>> pprint(merge_dicts({'a': 1}, {'b': 2}))
        {'a': 1, 'b': 2}
        >>> pprint(merge_dicts({'a': 1, 'b': 2}, {'b': 2}))
        {'a': 1, 'b': 2}

    More than two dictionaries may be merged as well::

        >>> pprint(merge_dicts({'a': 1, 'b': 2}, {'b': 2}, {'c':3}))
        {'a': 1, 'b': 2, 'c': 3}

    Error conditions::

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
