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
'''


from firmant import routing


__all__ = ['Type', 'Year', 'Month', 'Day', 'Slug', 'PageNo', 'year', 'month',
        'day', 'slug', 'pageno']


# Classes


class Type(routing.BoundNullPathComponent):
    '''The type of page that is to be matched.

    For instance, a type of ``post`` will only match pages that declare
    themselves to render posts.

    Example::

        >>> Type('post').match(type='post')
        True
        >>> Type('post').match(type='tag')
        False

    '''

    def __init__(self, value):
        super(Type, self).__init__('type', value)


class Year(routing.SinglePathComponent):
    '''A year associated with the page to be matched.

    Example::

        >>> Year().construct(year=2010)
        '2010'

    '''

    @classmethod
    def _conv(cls, value):
        return '%04i' % value

    def __init__(self):
        super(Year, self).__init__('year', self._conv)


class Month(routing.SinglePathComponent):
    '''A month associated with the page to be matched.

    Example::

        >>> Month().construct(month=3)
        '03'

    '''

    @classmethod
    def _conv(cls, value):
        return '%02i' % value

    def __init__(self):
        super(Month, self).__init__('month', self._conv)


class Day(routing.SinglePathComponent):
    '''A day associated with the page to be matched.

    Example::

        >>> Day().construct(day=15)
        '15'

    '''

    @classmethod
    def _conv(cls, value):
        return '%02i' % value

    def __init__(self):
        super(Day, self).__init__('day', self._conv)


class Slug(routing.SinglePathComponent):
    '''The slug associated with the page to be matched.

    Example::

        >>> Slug().construct(slug='foobar')
        'foobar'

    '''

    @classmethod
    def _conv(cls, value):
        return str(value)

    def __init__(self):
        super(Slug, self).__init__('slug', self._conv)


class PageNo(routing.SinglePathComponent):
    '''The page number associated with the page to be matched.

    Example::

        >>> PageNo().construct(page=1) is None
        True
        >>> PageNo().construct(page=2)
        'page2'

    '''

    @classmethod
    def _conv(cls, value):
        if value == 1:
            return None
        return 'page%i' % value

    def __init__(self):
        super(PageNo, self).__init__('page', self._conv)


# Convenient instances of all classes not tied to settings.


year    = Year()
month   = Month()
day     = Day()
slug    = Slug()
pageno  = PageNo()
