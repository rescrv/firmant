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
        d = merge_dicts(kwargs, *args)
        try:
            d = merge_dicts(d, self.bound_attributes)
        except ValueError:
            return False

        a = set(d.keys())
        b = self.attributes
        return a & b == a | b

    def construct(self, *args, **kwargs):
        raise RuntimeError("Not Implemented")


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
