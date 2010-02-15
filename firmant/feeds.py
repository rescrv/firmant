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

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.core import publish_programmatically
from docutils import io


__all__ = ['Feed', 'list_feeds', 'parse_feed']


slug_re = re.compile('^[a-zA-Z0-9][-\\_a-zA-Z0-9]{1,30}[a-zA-Z0-9]$')


class Feed(object):
    '''A Feed object.

    It is the core of the feed manipulation functions.
    '''

    __slots__ = ['_slug', '_title', '_subtitle', '_copyright', '_updated'
                ,'_entries']

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

    def get_slug(self):
        '''Return the slug of the feed as a unicode object.

            >>> f = Feed()
            >>> f.get_slug()

            >>> f = Feed(slug='rcos')
            >>> f.get_slug()
            u'rcos'

        '''
        return getattr(self, '_slug', None)

    def set_slug(self, val):
        '''Set the slug of the feed.

        Slugs must be composed of alphanumerics, numbers, hyphens and
        underscores.  The slug must start with an alphanumeric.

            >>> f = Feed()
            >>> f.set_slug('rcos')
            >>> f.get_slug()
            u'rcos'

            >>> # An invalid slug will raise a ValueError.
            >>> f = Feed()
            >>> f.set_slug('_rcos')
            Traceback (most recent call last):
            ValueError: Invalid slug.

        '''
        val = unicode(val)
        if slug_re.match(val) is None:
            raise ValueError('Invalid slug.')
        self._slug = val

    slug = property(get_slug, set_slug,
    doc='''The slug property.

    Access to the slug is mediated to validate that the slug always contains a
    valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Feed.get_slug`.
       - Set function: :func:`Feed.set_slug`.

    ''')

    def get_title(self):
        '''Return the title of the feed.

            >>> f = Feed()
            >>> f.get_title()

            >>> f = Feed(title='RCOS')
            >>> f.get_title()
            u'RCOS'

        '''
        return getattr(self, '_title', None)

    def set_title(self, val):
        '''Set the title of the feed.

            >>> f = Feed()
            >>> f.set_title('RCOS')
            >>> f.get_title()
            u'RCOS'

        '''
        self._title = unicode(val)

    title = property(get_title, set_title,
    doc='''The title property.

    Access to the title is mediated to validate that the title always contains a
    valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Feed.get_title`.
       - Set function: :func:`Feed.set_title`.

    ''')

    def get_subtitle(self):
        '''Return the subtitle of the feed.

            >>> f = Feed()
            >>> f.get_subtitle()

            >>> f = Feed(subtitle='RCOS')
            >>> f.get_subtitle()
            u'RCOS'

        '''
        return getattr(self, '_subtitle', None)

    def set_subtitle(self, val):
        '''Set the subtitle of the feed.

            >>> f = Feed()
            >>> f.set_subtitle('RCOS')
            >>> f.get_subtitle()
            u'RCOS'

        '''
        self._subtitle = unicode(val)

    subtitle = property(get_subtitle, set_subtitle,
    doc='''The subtitle property.

    Access to the subtitle is mediated to validate that the subtitle always
    contains a valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Feed.get_subtitle`.
       - Set function: :func:`Feed.set_subtitle`.

    ''')

    def get_copyright(self):
        '''Return the copyright information of the feed.

            >>> f = Feed()
            >>> f.get_copyright()

            >>> f = Feed(copyright=u'CC-BY-3.0')
            >>> f.get_copyright()
            u'CC-BY-3.0'

        '''
        return getattr(self, '_copyright', None)

    def set_copyright(self, val):
        '''Set the copyright information of the feed.

            >>> f = Feed()
            >>> f.set_copyright(u'CC-BY-3.0')
            >>> f.get_copyright()
            u'CC-BY-3.0'

        '''
        self._copyright = unicode(val)

    copyright = property(get_copyright, set_copyright,
    doc='''The copyright information property.

    Access to the copyright information is mediated to validate that the
    copyright information always is a valid unicode object (or ``None``).

    .. seealso::

       - Get function: :func:`Feed.get_copyright`.
       - Set function: :func:`Feed.set_copyright`.

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

    '''
    file = open(feed_path)
    data = file.read()
    file.close()
    parts, doc = publish_parts_doc(data)

    f = Feed()
    f.slug = os.path.basename(feed_path).rsplit('.', 1)[0]
    f.title = parts['title']
    f.subtitle = parts['subtitle']
    f.copyright = doc.copyright
    return f


class Copyright(Directive):

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        text = '\n'.join(self.content)
        self.state.document.copyright = text
        return []


directives.register_directive('copyright', Copyright)


def publish_parts_doc(source):
    args = {'source': source
           ,'source_path': None
           ,'source_class': io.StringInput
           ,'destination_class': io.StringOutput
           ,'destination': None
           ,'destination_path': None
           ,'reader': None, 'reader_name': 'standalone'
           ,'parser': None, 'parser_name': 'restructuredtext'
           ,'writer': None, 'writer_name': 'html'
           ,'settings': None, 'settings_spec': None, 'settings_overrides': None
           ,'config_section': None
           ,'enable_exit_status': None
           }
    output, pub = publish_programmatically(**args)
    return pub.writer.parts, pub.document
