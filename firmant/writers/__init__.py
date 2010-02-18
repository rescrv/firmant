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


import collections
import logging

from firmant.i18n import _
from firmant.utils import class_name


class Writer(object):
    '''Transform a parsed blog into objects on the file system.

        >>> from firmant.parser import Blog
        >>> b = Blog('content', lambda w: None, lambda e: None)
        >>> w = Writer({'settings': True}, b)
        >>> w #doctest: +ELLIPSIS
        <firmant.writers.Writer object at 0x...>

    '''

    def __init__(self, settings, blog):
        self.settings = settings
        self.entries = blog._entries
        self.feeds = blog._feeds
        self.tags = blog._tags
        self.log = logging.getLogger(class_name(self.__class__))

    def write(self):
        pass

    def write_preconditions(self):
        '''Returns true if and only if it is acceptable to proceed with writing.
        '''
        # Fail if we do not have an output directory.
        if self.settings.get('OUTPUT_DIR', None) is None:
            self.log.critical(_('``OUTPUT_DIR`` not defined in settings.'))
            return False
        return True


class EntryWriter(Writer):
    '''Parse the entries pertaining to a blog.

    This class is simply a subclass of :class:`Writer` used for abstracting some
    common functions.
    '''

    def path(self, entry):
        '''Return the path for the entry.
        '''
        # Hackish, but works around the python strftime bug.
        dt = entry.published.date()
        return '%04i/%02i/%02i/%s' % (dt.year, dt.month, dt.day, entry.slug)

    def log_processing(self, entry):
        '''Log to the info logger that we are processing entries.
        '''
        self.log.info(_('processing post: %s') % self.path(entry))

    @classmethod
    def split_years(cls, entries):
        '''Return a list of tuples.  They will be of the form:
        [(YYYY, [<entries>, ...]), ...]

            >>> import datetime
            >>> from pprint import pprint
            >>> from firmant.entries import Entry
            >>> a = Entry(published=datetime.datetime(2008, 1, 1), slug='aaa')
            >>> b = Entry(published=datetime.datetime(2009, 1, 1), slug='baa')
            >>> c = Entry(published=datetime.datetime(2009, 1, 1), slug='caa')
            >>> d = Entry(published=datetime.datetime(2010, 1, 1), slug='daa')
            >>> e = Entry(published=datetime.datetime(2010, 1, 1), slug='eaa')
            >>> f = Entry(published=datetime.datetime(2010, 1, 1), slug='faa')
            >>> pprint(EntryWriter.split_years([a, b, c, d, e])) #doctest: +ELLIPSIS
            [(2008, [<firmant.entries.Entry object at 0x...>]),
             (2009,
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>]),
             (2010,
              [<firmant.entries.Entry object at 0x...>,
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
            >>> a = Entry(published=datetime.datetime(2009, 1, 1), slug='aaa')
            >>> b = Entry(published=datetime.datetime(2009, 2, 1), slug='baa')
            >>> c = Entry(published=datetime.datetime(2009, 2, 1), slug='caa')
            >>> d = Entry(published=datetime.datetime(2010, 1, 1), slug='daa')
            >>> e = Entry(published=datetime.datetime(2010, 1, 1), slug='eaa')
            >>> f = Entry(published=datetime.datetime(2010, 1, 1), slug='faa')
            >>> pprint(EntryWriter.split_months([a, b, c, d, e])) #doctest: +ELLIPSIS
            [((2009, 1), [<firmant.entries.Entry object at 0x...>]),
             ((2009, 2),
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>]),
             ((2010, 1),
              [<firmant.entries.Entry object at 0x...>,
               <firmant.entries.Entry object at 0x...>])]

        '''
        d = collections.defaultdict(list)
        for year, entries in cls.split_years(entries):
            for entry in entries:
                d[(year, entry.published.month)].append(entry)
        return [(x, sorted(y)) for x, y in sorted(d.items())]
