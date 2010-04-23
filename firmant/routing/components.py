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


'''Predefined path components for use with URLMapper.

Each of these pre-built components is meant for exactly one use case.  The
attributes (both free and bound) are shown, and then the various behaviors are
shown.  All should be self-explanatory.

TYPE
====

.. doctest::

   >>> TYPE('post').attributes
   set(['type'])
   >>> TYPE('post').bound_attributes
   {'type': 'post'}
   >>> TYPE('post').free_attributes
   set([])

   >>> TYPE('post').match(type='post')
   True
   >>> TYPE('post').match(type='tag')
   False

YEAR
====

.. doctest::

   >>> YEAR.attributes
   set(['year'])
   >>> YEAR.bound_attributes
   {}
   >>> YEAR.free_attributes
   set(['year'])

   >>> YEAR.construct(year=2010)
   '2010'
   >>> YEAR.construct(year=4)
   '0004'

MONTH
=====

.. doctest::

   >>> MONTH.attributes
   set(['month'])
   >>> MONTH.bound_attributes
   {}
   >>> MONTH.free_attributes
   set(['month'])

   >>> MONTH.construct(month=10)
   '10'
   >>> MONTH.construct(month=3)
   '03'

DAY
===

.. doctest::

   >>> DAY.attributes
   set(['day'])
   >>> DAY.bound_attributes
   {}
   >>> DAY.free_attributes
   set(['day'])

   >>> DAY.construct(day=15)
   '15'
   >>> DAY.construct(day=1)
   '01'

SLUG
====

.. doctest::

   >>> SLUG.attributes
   set(['slug'])
   >>> SLUG.bound_attributes
   {}
   >>> SLUG.free_attributes
   set(['slug'])

   >>> SLUG.construct(slug='foobar')
   'foobar'

PATH
====

.. doctest::

   >>> PATH.attributes
   set(['path'])
   >>> PATH.bound_attributes
   {}
   >>> PATH.free_attributes
   set(['path'])

   >>> PATH.construct(path='foo/bar')
   'foo/bar'

PAGENO
======

.. doctest::

   >>> PAGENO.attributes
   set(['page'])
   >>> PAGENO.bound_attributes
   {}
   >>> PAGENO.free_attributes
   set(['page'])

   >>> PAGENO.construct(page=1) is None
   True
   >>> PAGENO.construct(page=2)
   'page2'

'''


import functools

from firmant import routing


__all__ = ['TYPE', 'YEAR', 'MONTH', 'DAY', 'SLUG', 'PATH', 'PAGENO']


TYPE  = functools.partial(routing.BoundNullPathComponent, 'type')
YEAR  = routing.SinglePathComponent('year', lambda y: '%04i' % y)
MONTH = routing.SinglePathComponent('month', lambda m: '%02i' % m)
DAY   = routing.SinglePathComponent('day', lambda d: '%02i' % d)
SLUG  = routing.SinglePathComponent('slug', str)
PATH  = routing.SinglePathComponent('path', str)


def __page_conv__(value):
    if value == 1:
        return None
    return 'page%i' % value
PAGENO = routing.SinglePathComponent('page', __page_conv__)
