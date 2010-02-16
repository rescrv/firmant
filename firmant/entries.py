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


'''Manipulate entry objects for Firmant.
'''


import datetime
import os
import re

from firmant import du
from firmant import properties


__all__ = ['Entry', 'list_entries']


slug_re = re.compile('^[a-zA-Z0-9][-\\_a-zA-Z0-9.]{1,30}[a-zA-Z0-9]$')


class Entry(object):
    '''An Entry object.

    It is the core of the entry manipulation functions.
    '''

    __slots__ = ['_slug', '_published', '_author', '_tags', '_feeds'
                ,'_copyright', '_updated', '_title', '_content'
                ,'_tz']

    def __init__(self, **kwargs):
        '''Construct a new Entry.  Optional kwargs are used to populate the data
        members.

            >>> # Create a new Entry object and specify all fields.
            >>> d = {'slug': 'firmant-nears-0.1'
            ...     ,'published': datetime.datetime(2010, 2, 15, 13, 9)
            ...     ,'author': 'Robert Escriva'
            ...     ,'tags': ['firmant', 'rcos']
            ...     ,'feeds': ['firmant', 'rcos', 'python']
            ...     ,'copyright': 'CC-BY-3.0'
            ...     ,'updated': datetime.datetime(2010, 2, 15, 13, 12)
            ...     ,'title': 'Firmant nears a 0.1 release'
            ...     ,'content': 'As development progresses, ...'
            ...     ,'tz': 'America/New_York'
            ...     }
            >>> Entry(**d) #doctest: +ELLIPSIS
            <firmant.entries.Entry object at 0x...>

            >>> # KeyError will be thrown if invalid arguments are passed.
            >>> Entry(noexist=True)
            Traceback (most recent call last):
            KeyError: "Invalid key ''noexist'' found in kwargs."

        '''
        defaults = {'slug': None
                   ,'published': None
                   ,'author': None
                   ,'tags': list()
                   ,'feeds': list()
                   ,'copyright': None
                   ,'updated': None
                   ,'title': None
                   ,'content': None
                   ,'tz': None
                   }
        defaults.update(kwargs)
        for key, value in kwargs.items():
            if '_' + key not in self.__slots__:
                raise KeyError("Invalid key '%s' found in kwargs." % repr(key))
            else:
                setattr(self, key, value)

    slug = properties.property_regex('_slug', 'slug', slug_re,
    doc='''The slug property.

    Access to the slug is mediated to validate that the slug always contains a
    valid unicode object (or ``None``).

        >>> e = Entry()
        >>> e.slug
        >>> e.slug = u'rcos'
        >>> e.slug
        u'rcos'

        >>> # Assigning None will set the slug to None
        >>> e.slug = None
        >>> e.slug

        >>> # An invalid slug will raise a ValueError.
        >>> e = Entry()
        >>> e.slug = '_rcos'
        Traceback (most recent call last):
        ValueError: Invalid value for 'slug'.  Failed to match regex.

    ''')

    published = properties.property_datetime('_published', 'published',
    doc='''The published property.

    Access to the update time is mediated to validate that the publication time
    always contains is valid :class:`datetime.datetime` object.

        >>> e = Entry()
        >>> e.published
        >>> e.published = None
        >>> e.published

        >>> e = Entry()
        >>> e.published
        >>> e.published = datetime.datetime(2010, 2, 15, 18, 7)
        >>> e.published
        datetime.datetime(2010, 2, 15, 18, 7)

        >>> e = Entry()
        >>> e.published = '2010-02-15 18:07:04'
        >>> e.published
        datetime.datetime(2010, 2, 15, 18, 7, 4)

        >>> # Also works if seconds are ommitted.
        >>> e = Entry()
        >>> e.published = '2010-02-15 18:07'
        >>> e.published
        datetime.datetime(2010, 2, 15, 18, 7)

        >>> # Passing something other than a datetime object or string, raise a
        >>> # TypeError
        >>> e.published = 'not a date'
        Traceback (most recent call last):
        ValueError: time data 'not a date' does not match format '%Y-%m-%d %H:%M:%S'

    ''')

    author = properties.property_unicode('_author', 'author',
    doc='''The author property.

    Access to the author is mediated to validate that the author always is
    a valid unicode object (or ``None``).

        >>> e = Entry()
        >>> e.author
        >>> e.author = None
        >>> e.author

        >>> e = Entry(author='Robert')
        >>> e.author
        u'Robert'

        >>> e = Entry()
        >>> e.author = 'Robert'
        >>> e.author
        u'Robert'

    ''')

    tags = properties.property_iterable('_tags', 'tags',
    doc='''The tags property.

    Access to the tags is mediated to validate that the tags always are a valid
    iterable object.

        >>> e = Entry()
        >>> e.tags
        []

        >>> # Assigning None simply empties the list.
        >>> e = Entry()
        >>> e.tags = None
        >>> e.tags
        []

        >>> e.tags = ['foo', 'bar', 'baz']
        >>> e.tags
        ['foo', 'bar', 'baz']

        >>> # Raise a TypeError when assigned a non-iterable.
        >>> e.tags = 1
        Traceback (most recent call last):
        TypeError: 'int' object is not iterable
    ''')

    feeds = properties.property_iterable('_feeds', 'feeds',
    doc='''The feeds property.

    Access to the feeds is mediated to validate that the feeds always are a
    valid iterable object.

        >>> e = Entry()
        >>> e.feeds
        []

        >>> # Assigning None simply empties the list.
        >>> e = Entry()
        >>> e.feeds = None
        >>> e.feeds
        []

        >>> e.feeds = ['foo', 'bar', 'baz']
        >>> e.feeds
        ['foo', 'bar', 'baz']

        >>> # Raise a TypeError when assigned a non-iterable.
        >>> e.feeds = 1
        Traceback (most recent call last):
        TypeError: 'int' object is not iterable
    ''')

    copyright = properties.property_unicode('_copyright', 'copyright',
    doc='''The copyright information property.

    Access to the copyright information is mediated to validate that the
    copyright information always is a valid unicode object (or ``None``).

        >>> e = Entry()
        >>> e.copyright
        >>> e.copyright = None
        >>> e.copyright

        >>> e = Entry(copyright='CC-BY-3.0')
        >>> e.copyright
        u'CC-BY-3.0'

        >>> e = Entry()
        >>> e.copyright = 'CC-BY-3.0'
        >>> e.copyright
        u'CC-BY-3.0'

    ''')

    def get_updated(self):
        '''Return the update time of the entry.

            >>> e = Entry()
            >>> e.get_updated()

            >>> now = datetime.datetime.now()
            >>> e = Entry(updated=now)
            >>> e.get_updated() == now
            True

        '''
        return getattr(self, '_updated', None)

    def set_updated(self, val):
        '''Set the update time of the entry.

            >>> e = Entry()
            >>> now = datetime.datetime.now()
            >>> e.set_updated(now)
            >>> e.get_updated() == now
            True

            >>> # Passing something other than a datetime object throws a
            >>> # TypeError
            >>> e.set_updated('not a date')
            Traceback (most recent call last):
            TypeError: Val is not of the correct type.

        '''
        if val is not None and not isinstance(val, datetime.datetime):
            raise TypeError('Val is not of the correct type.')
        self._updated = val

    updated = property(get_updated, set_updated,
    doc='''The updated property.

    Access to the update time is mediated to validate that the update time
    always contains is valid datetime object (or ``None``).

    .. seealso::

       - Get function: :func:`Entry.get_updated`.
       - Set function: :func:`Entry.set_updated`.

    ''')

    def get_title(self):
        '''Return the title of the entry.

            >>> e = Entry()
            >>> e.get_title()

            >>> e = Entry(title='A rework of Firmant for RCOS.')
            >>> e.get_title()
            u'A rework of Firmant for RCOS.'

        '''
        return getattr(self, '_title', None)

    def set_title(self, val):
        '''Set the title of the entry.

            >>> f = Entry()
            >>> f.set_title('A rework of Firmant for RCOS.')
            >>> f.get_title()
            u'A rework of Firmant for RCOS.'

        '''
        self._title = unicode(val)

    title = property(get_title, set_title,
    doc='''The title property.

    Access to the title is mediated to validate that the title always contains a
    valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Entry.get_title`.
       - Set function: :func:`Entry.set_title`.

    ''')

    def get_content(self):
        '''Return the content of the entry.

            >>> e = Entry()
            >>> e.get_content()

            >>> e = Entry(content='A rework of Firmant for RCOS.')
            >>> e.get_content()
            u'A rework of Firmant for RCOS.'

        '''
        return getattr(self, '_content', None)

    def set_content(self, val):
        '''Set the content of the entry.

            >>> f = Entry()
            >>> f.set_content('A rework of Firmant for RCOS.')
            >>> f.get_content()
            u'A rework of Firmant for RCOS.'

        '''
        self._content = unicode(val)

    content = property(get_content, set_content,
    doc='''The content property.

    Access to the content is mediated to validate that the content always
    contains a valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Entry.get_content`.
       - Set function: :func:`Entry.set_content`.

    ''')

    def get_tz(self):
        '''Return the timezone of the entry.

            >>> e = Entry()
            >>> e.get_tz()

            >>> e = Entry(tz='A rework of Firmant for RCOS.')
            >>> e.get_tz()
            u'A rework of Firmant for RCOS.'

        '''
        return getattr(self, '_tz', None)

    def set_tz(self, val):
        '''Set the timezone of the entry.

            >>> f = Entry()
            >>> f.set_tz('A rework of Firmant for RCOS.')
            >>> f.get_tz()
            u'A rework of Firmant for RCOS.'

        '''
        self._tz = unicode(val)

    tz = property(get_tz, set_tz,
    doc='''The timezone property.

    Access to the timezone is mediated to validate that the timezone always
    contains a valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Entry.get_tz`.
       - Set function: :func:`Entry.set_tz`.

    ''')


def list_entries(content_root, subdir='posts', suffix='.rst'):
    '''Generate the absolute path for each entry object.

    Consider all the contents of the entries directory (by default this is
    ``content_root/entries``).  Only files ending in ``suffix`` are considered.

    Entries that are not files are ignored.

        >>> from pprint import pprint
        >>> pprint(list_entries('content'))
        ['content/posts/1775-03-23-give-me-liberty.rst',
         'content/posts/2009-02-17-loren-ipsum.rst',
         'content/posts/2010-02-13-sample-code.rst']


    '''

    path  = os.path.join(content_root, subdir)
    files = os.listdir(path)
    files = map(lambda p: os.path.join(path, p), files)
    files = filter(lambda f: f.endswith(suffix), files)
    files = filter(lambda f: os.path.isfile(f), files)
    files.sort()
    return files


def parse_entry(entry_path):
    '''Construct an entry object from the entry on the file system.

    This does not load any information other than that which is stored in the
    ``/entries/`` directory.

        >>> e = parse_entry('content/posts/1775-03-23-give-me-liberty.rst')
        >>> e.slug
        u'give-me-liberty'
        >>> e.published
        datetime.datetime(1775, 3, 23, 13, 1)
        >>> e.author
        u'Patrick Henry'
        >>> e.tags
        [u'speech', u'patriotism']
        >>> e.feeds
        ['default']
        >>> e.copyright
        u'This document is part of the public domain.'
        >>> e.updated
        datetime.datetime(2009, 2, 17, 11, 31)
        >>> e.title
        u'Give Me Liberty or Give Me Death'
        >>> e.content #doctest: +ELLIPSIS
        u'<p>No man thinks more highly ... or give me death.</p>\\n'
        >>> e.tz
        u'US/Eastern'

    '''
    file = open(entry_path)
    data = file.read()
    file.close()
    parts, doc = du.publish_parts_doc(data)

    e = Entry()
    e.slug, null = os.path.basename(entry_path)[11:].rsplit('.', 1)
    dt = datetime.datetime.strptime(os.path.basename(entry_path)[:10],
    '%Y-%m-%d')
    e.published = datetime.datetime.combine(dt.date(), doc.time)
    e.author = doc.author
    e.tags = doc.tags
    if hasattr(doc, 'nodefaultfeed'):
        e.feeds = list()
    else:
        e.feeds = list(['default'])
    e.title = parts['title']
    e.title = parts['title']
    e.content = parts['fragment']
    e.copyright = doc.copyright
    e.updated = doc.updated
    e.tz = doc.timezone
    return e
