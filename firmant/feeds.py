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


'''Manipulate feed objects for Firmant.
'''


import datetime
import os
import re

from firmant import du
from firmant import properties


__all__ = ['Feed', 'list_feeds', 'parse_feed']


slug_re = re.compile('^[a-zA-Z0-9][-\\_a-zA-Z0-9]{1,30}[a-zA-Z0-9]$')


class Feed(object):
    '''A Feed object.

    It is the core of the feed manipulation functions.
    '''

    __slots__ = ['_slug', '_title', '_subtitle', '_copyright', '_updated'
                ,'_entries', '_body']

    def __init__(self, **kwargs):
        '''Construct a new Feed.  Optional kwargs are used to populate the data
        members.

            >>> # Create a new Feed object and specify all fields.
            >>> d = {'slug': 'rcos'
            ...     ,'title': 'RCOS'
            ...     ,'subtitle': 'The Rensselaer Center for Open Source'
            ...     ,'copyright': 'Creative Commons Attribution 3.0 Unported'
            ...     ,'updated': datetime.datetime.now()
            ...     ,'entries': list()
            ...     }
            >>> Feed(**d) #doctest: +ELLIPSIS
            <firmant.feeds.Feed object at 0x...>

            >>> # KeyError will be thrown if invalid arguments are passed.
            >>> Feed(noexist=True)
            Traceback (most recent call last):
            KeyError: "Invalid key ''noexist'' found in kwargs."

        '''
        defaults = {'slug': None
                   ,'title': None
                   ,'subtitle': None
                   ,'copyright': None
                   ,'updated': None
                   ,'entries': list()
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

        >>> f = Feed()
        >>> f.slug
        >>> f.slug = u'rcos'
        >>> f.slug
        u'rcos'

        >>> # Assigning None will set the slug to None
        >>> f.slug = None
        >>> f.slug

        >>> # An invalid slug will raise a ValueError.
        >>> f = Feed()
        >>> f.slug = '_rcos'
        Traceback (most recent call last):
        ValueError: Invalid value for 'slug'.  Failed to match regex.

    ''')

    title = properties.property_unicode('_title', 'title',
    doc='''The title property.

    Access to the title is mediated to validate that the title always contains a
    valid unicode object (or ``None``).

        >>> f = Feed()
        >>> f.title
        >>> f.title = None
        >>> f.title

        >>> f = Feed(title='RCOS')
        >>> f.title
        u'RCOS'

        >>> f = Feed()
        >>> f.title = 'RCOS'
        >>> f.title
        u'RCOS'

    ''')

    subtitle = properties.property_unicode('_subtitle', 'subtitle',
    doc='''The subtitle property.

    Access to the subtitle is mediated to validate that the subtitle always
    contains a valid unicode object (or ``None``).

        >>> f = Feed()
        >>> f.subtitle
        >>> f.subtitle = None
        >>> f.subtitle

        >>> f = Feed(subtitle='Rensselaer Center For Open Source')
        >>> f.subtitle
        u'Rensselaer Center For Open Source'

        >>> f = Feed()
        >>> f.subtitle = 'Rensselaer Center For Open Source'
        >>> f.subtitle
        u'Rensselaer Center For Open Source'

    ''')

    copyright = properties.property_unicode('_copyright', 'copyright',
    doc='''The copyright information property.

    Access to the copyright information is mediated to validate that the
    copyright information always is a valid unicode object (or ``None``).

        >>> f = Feed()
        >>> f.copyright
        >>> f.copyright = None
        >>> f.copyright

        >>> f = Feed(copyright='CC-BY-3.0')
        >>> f.copyright
        u'CC-BY-3.0'

        >>> f = Feed()
        >>> f.copyright = 'CC-BY-3.0'
        >>> f.copyright
        u'CC-BY-3.0'

    ''')

    def get_updated(self):
        '''Return the update time of the feed.

            >>> f = Feed()
            >>> f.get_updated()

            >>> now = datetime.datetime.now()
            >>> f = Feed(updated=now)
            >>> f.get_updated() == now
            True

        '''
        return getattr(self, '_updated', None)

    def set_updated(self, val):
        '''Set the update time of the feed.

            >>> f = Feed()
            >>> now = datetime.datetime.now()
            >>> f.set_updated(now)
            >>> f.get_updated() == now
            True

            >>> # Passing something other than a datetime object throws a
            >>> # TypeError
            >>> f.set_updated('not a date')
            Traceback (most recent call last):
            TypeError: Val is not of the correct type.

        '''
        if val is not None and not isinstance(val, datetime.datetime):
            raise TypeError('Val is not of the correct type.')
        self._updated = val

    updated = property(get_updated, set_updated,
    doc='''The updated property.

    Access to the update time is mediated to validate that the update time
    always contains is valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Feed.get_updated`.
       - Set function: :func:`Feed.set_updated`.

    ''')

    def get_entries(self):
        '''Return the entries of the feed.

            >>> f = Feed()
            >>> f.get_entries()
            []

            >>> f = Feed(entries=list())
            >>> f.get_entries()
            []

        '''
        return getattr(self, '_updated', list())

    def set_entries(self, val):
        '''Set the entries of the feed.

            >>> f = Feed()
            >>> f.set_entries(list())
            >>> f.get_entries()
            []

        '''
        self._entries = list(val)

    entries = property(get_entries, set_entries,
    doc='''The entries property.

    Access to the entries is mediated to validate that the entries always
    contains a valid list object.

    .. seealso::

       - Get function: :func:`Feed.get_entries`.
       - Set function: :func:`Feed.set_entries`.

    ''')

    body = properties.property_unicode('_body', 'body',
    doc='''The body property.

    Access to the body is mediated to validate that the body always contains a
    valid unicode object (or ``None``).

        >>> f = Feed()
        >>> f.body
        >>> f.body = None
        >>> f.body

        >>> f = Feed(body='The body of the feed displayed on html pages.')
        >>> f.body
        u'The body of the feed displayed on html pages.'

        >>> f = Feed()
        >>> f.body = 'The body of the feed displayed on html pages.'
        >>> f.body
        u'The body of the feed displayed on html pages.'

    ''')



def list_feeds(content_root, feed_subdir='feeds', suffix='.rst'):
    '''Generate the absolute path for each feed object.

    Consider all the contents of the feeds directory (by default this is
    ``content_root/feeds``).  Only files ending in ``suffix`` are considered.

    Entries that are not files are ignored.

        >>> list_feeds('content')
        ['content/feeds/rcos.rst']

    '''

    path  = os.path.join(content_root, feed_subdir)
    files = os.listdir(path)
    files = map(lambda p: os.path.join(path, p), files)
    files = filter(lambda f: f.endswith(suffix), files)
    files = filter(lambda f: os.path.isfile(f), files)
    files.sort()
    return files


def parse_feed(feed_path):
    '''Construct a feed object from the feed on the file system.

    This does not load any information other than that which is stored in the
    ``/feeds/`` directory.

        >>> f = parse_feed('content/feeds/rcos.rst')
        >>> f.slug
        u'rcos'
        >>> f.title
        u'The feed should be titled RCOS'
        >>> f.subtitle
        u'Information pertaining to RCOS'
        >>> f.copyright
        u'Feeds can have explicit copyright too.'
        >>> f.updated
        >>> f.entries
        []
        >>> f.body
        u'<p>The body of the feed displayed on html pages.</p>\\n'

    '''
    file = open(feed_path)
    data = file.read()
    file.close()
    parts, doc = du.publish_parts_doc(data)

    f = Feed()
    f.slug = os.path.basename(feed_path).rsplit('.', 1)[0]
    f.title = parts['title']
    f.subtitle = parts['subtitle']
    f.copyright = doc.copyright
    f.body = parts['fragment']
    return f
