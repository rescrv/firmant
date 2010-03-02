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


class EntryWriter(Writer):
    '''Parse the entries pertaining to a blog.

    This class is simply a subclass of :class:`Writer` used for abstracting some
    common functions.
    '''

    @classmethod
    def split_years(cls, entries):
        '''Return a list of tuples.  They will be of the form:
        [(YYYY, [<entries>, ...]), ...]

            >>> import datetime
            >>> from pprint import pprint
            >>> from firmant.entries import Entry
            >>> a = Entry(published=datetime.datetime(2008, 1, 7), slug='aaa')
            >>> b = Entry(published=datetime.datetime(2009, 2, 8), slug='baa')
            >>> c = Entry(published=datetime.datetime(2009, 3, 9), slug='caa')
            >>> d = Entry(published=datetime.datetime(2010, 4, 1), slug='daa')
            >>> e = Entry(published=datetime.datetime(2010, 5, 2), slug='eaa')
            >>> f = Entry(published=datetime.datetime(2010, 6, 3), slug='faa')
            >>> pprint(EntryWriter.split_years([a, b, c, d, e, f])) #doctest: +ELLIPSIS
            [(2008, [<firmant.entries.Entry object at 0x...>]),
             (2009,
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>]),
             (2010,
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>])]

        '''
        d = collections.defaultdict(list)
        for entry in entries:
            d[entry.published.year].append(entry)
        return [(x, sorted(y)) for x, y in sorted(d.items())]

    @classmethod
    def split_months(cls, entries):
        '''Return a list of tuples.  They will be of the form:
        [((YYYY, MM), [<entries>, ...]), ...]

            >>> import datetime
            >>> from pprint import pprint
            >>> from firmant.entries import Entry
            >>> a = Entry(published=datetime.datetime(2010, 1, 1), slug='aaa')
            >>> b = Entry(published=datetime.datetime(2010, 2, 2), slug='baa')
            >>> c = Entry(published=datetime.datetime(2010, 2, 3), slug='caa')
            >>> d = Entry(published=datetime.datetime(2010, 3, 4), slug='daa')
            >>> e = Entry(published=datetime.datetime(2010, 3, 5), slug='eaa')
            >>> f = Entry(published=datetime.datetime(2010, 3, 6), slug='faa')
            >>> pprint(EntryWriter.split_months([a, b, c, d, e, f])) #doctest: +ELLIPSIS
            [((2010, 1), [<firmant.entries.Entry object at 0x...>]),
             ((2010, 2),
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>]),
             ((2010, 3),
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>])]

        '''
        d = collections.defaultdict(list)
        for year, entries in cls.split_years(entries):
            for entry in entries:
                d[(year, entry.published.month)].append(entry)
        return [(x, sorted(y)) for x, y in sorted(d.items())]

    @classmethod
    def split_days(cls, entries):
        '''Return a list of tuples.  They will be of the form:
        [((YYYY, MM), [<entries>, ...]), ...]

            >>> import datetime
            >>> from pprint import pprint
            >>> from firmant.entries import Entry
            >>> a = Entry(published=datetime.datetime(2010, 1, 1), slug='aaa')
            >>> b = Entry(published=datetime.datetime(2010, 1, 2), slug='baa')
            >>> c = Entry(published=datetime.datetime(2010, 1, 2), slug='caa')
            >>> d = Entry(published=datetime.datetime(2010, 1, 3), slug='daa')
            >>> e = Entry(published=datetime.datetime(2010, 1, 3), slug='eaa')
            >>> f = Entry(published=datetime.datetime(2010, 1, 3), slug='faa')
            >>> pprint(EntryWriter.split_days([a, b, c, d, e, f])) #doctest: +ELLIPSIS
            [((2010, 1, 1), [<firmant.entries.Entry object at 0x...>]),
             ((2010, 1, 2),
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>]),
             ((2010, 1, 3),
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>])]

        '''
        d = collections.defaultdict(list)
        for (year, month), entries in cls.split_months(entries):
            for entry in entries:
                d[(year, month, entry.published.day)].append(entry)
        return [(x, sorted(y)) for x, y in sorted(d.items())]
