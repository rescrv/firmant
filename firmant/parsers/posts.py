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


'''Manipulate post objects for Firmant.
'''


import datetime
import os

from firmant.parsers import RstParser
from firmant.parsers import RstObject
from firmant.utils import strptime


__all__ = ['PostParser']


class PostParser(RstParser):
    '''Interpret *.rst for a given directory.

    For each reSt document, parse it to a post and extract its metadata.

        >>> p = PostParser()
        >>> p = p.parse_one('content/posts/1975-03-23-give-me-liberty.rst')
        >>> p.slug
        u'give-me-liberty'
        >>> p.published
        datetime.datetime(1975, 3, 23, 13, 1)
        >>> p.author
        u'Patrick Henry'
        >>> p.tags
        [u'speech', u'patriotism']
        >>> p.feeds
        [u'patriotic-things']
        >>> p.copyright
        u'This document is part of the public domain.'
        >>> p.updated
        datetime.datetime(2009, 2, 17, 11, 31)
        >>> p.title
        u'Give Me Liberty or Give Me Death'
        >>> p.content #doctest: +ELLIPSIS
        u"<p>Two hundred years ago people ... or give me death.</p>\\n"
        >>> p.tz
        u'US/Eastern'

    Default values (except published/updated/slug)::

        >>> p = PostParser()
        >>> p = p.parse_one('content/posts/2010-02-15-empty.rst')
        >>> p.slug
        u'empty'
        >>> p.published
        datetime.datetime(2010, 2, 15, 0, 0)
        >>> p.author
        u''
        >>> p.tags
        []
        >>> p.feeds
        []
        >>> p.copyright
        u''
        >>> p.updated
        datetime.datetime(2010, 2, 15, 0, 0)
        >>> p.title
        u''
        >>> p.content #doctest: +ELLIPSIS
        u''
        >>> p.tz
        u''

    All posts may be retrieved with::

        >>> from pysettings.settings import Settings
        >>> s = {'CONTENT_ROOT': 'content'
        ...     ,'POSTS_SUBDIR': 'posts'
        ...     ,'REST_EXTENSION': 'rst'
        ...     }
        >>> s = Settings(s)
        >>> p = PostParser(s)
        >>> p.log = Mock('log')
        >>> pprint(map(lambda p: (p.published.date(), p.slug), p.parse()))
        Called log.info('parsed content/posts/1975-03-23-give-me-liberty.rst')
        Called log.info('parsed content/posts/2009-02-17-loren-ipsum.rst')
        Called log.info('parsed content/posts/2010-02-13-sample-code.rst')
        Called log.info('parsed content/posts/2010-02-15-empty.rst')
        [(datetime.date(1975, 3, 23), u'give-me-liberty'),
         (datetime.date(2009, 2, 17), u'loren-ipsum'),
         (datetime.date(2010, 2, 13), u'sample-code'),
         (datetime.date(2010, 2, 15), u'empty')]

    '''

    auto_metadata = [('author', 'author')
                    ,('tags', 'tags')
                    ,('feeds', 'feeds')
                    ,('copyright', 'copyright')
                    ,('updated', 'updated')
                    ,('tz', 'timezone')
                    ]

    auto_pubparts = [('title', 'title')
                    ,('content', 'fragment')
                    ]

    def paths(self):
        '''Return a list of paths to objects on the file system.

        Consider all the contents of the posts directory (by default this is
        ``content_root/posts``).  Only files ending in ``suffix`` are
        considered.

        Directory entries that are not files are ignored.

            >>> from pysettings.settings import Settings
            >>> s = {'CONTENT_ROOT': 'content'
            ...     ,'POSTS_SUBDIR': 'posts'
            ...     ,'REST_EXTENSION': 'rst'
            ...     }
            >>> s = Settings(s)
            >>> p = PostParser(s)
            >>> pprint(p.paths())
            ['content/posts/1975-03-23-give-me-liberty.rst',
             'content/posts/2009-02-17-loren-ipsum.rst',
             'content/posts/2010-02-13-sample-code.rst',
             'content/posts/2010-02-15-empty.rst']

        '''
        # TODO add above settings to global settings.
        settings = self.settings
        path  = os.path.join(settings.CONTENT_ROOT, settings.POSTS_SUBDIR)
        files = os.listdir(path)
        files = map(lambda p: os.path.join(path, p), files)
        files = filter(lambda f: f.endswith(settings.REST_EXTENSION), files)
        files = filter(lambda f: os.path.isfile(f), files)
        files.sort()
        return files

    def new_object(self, path, d, pub):
        '''Return an instance of the object to which rst documents are parsed.
        '''
        p = RstObject()
        p.slug, null = os.path.basename(path)[11:].rsplit('.', 1)
        p.slug = unicode(p.slug)
        dt = strptime(os.path.basename(path)[:10], ['%Y-%m-%d'])
        if 'time' in d:
            t = d['time']
        else:
            t = datetime.time(0, 0, 0)
        p.published = datetime.datetime.combine(dt.date(), t)
        p.updated = p.published
        return p

    def default(self, attr):
        '''Return the default value of an attribute.
        '''
        d = {'tags': list()
            ,'feeds': list()
            }
        return d.get(attr, u'')

    def post_process(self, doc):
        '''Cleanup the update timestamp.
        '''
        if doc.updated == u'':
            doc.updated = doc.published
