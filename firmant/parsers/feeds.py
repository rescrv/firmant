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


import os

from firmant.parsers import RstParser
from firmant.parsers import RstObject


__all__ = ['FeedParser']


class FeedParser(RstParser):
    '''Interpret *.rst for a given feed directory.

    For each reSt document, parse it to a feed and extract its metadata.

        >>> f = FeedParser()
        >>> f = f.parse_one('content/feeds/rcos.rst')
        >>> f.slug
        u'rcos'
        >>> f.title
        u'The feed should be titled RCOS'
        >>> f.subtitle
        u'Information pertaining to RCOS'
        >>> f.copyright
        u'Feeds can have explicit copyright too.'
        >>> f.body
        u'<p>The body of the feed displayed on html pages.</p>\\n'

    Default values (except slug)::

        >>> # Test the empty-file case.
        >>> f = FeedParser()
        >>> f = f.parse_one('content/feeds/empty.rst')
        >>> f.slug
        u'empty'
        >>> f.title
        u''
        >>> f.subtitle
        u''
        >>> f.copyright
        u''
        >>> f.body
        u''

    Note that posts are not cross-referenced at this point.  This also implies
    that the update time is not set::

        >>> f.posts
        Traceback (most recent call last):
        AttributeError: 'RstObject' object has no attribute 'posts'
        >>> f.updated
        Traceback (most recent call last):
        AttributeError: 'RstObject' object has no attribute 'updated'

    All feeds may be retrieved with::

        >>> from pysettings.settings import Settings
        >>> s = {'CONTENT_ROOT': 'content'
        ...     ,'FEEDS_SUBDIR': 'feeds'
        ...     ,'REST_EXTENSION': 'rst'
        ...     }
        >>> s = Settings(s)
        >>> f = FeedParser(s)
        >>> f.log = Mock('log')
        >>> map(lambda f: f.slug, f.parse())
        Called log.info('parsed content/feeds/empty.rst')
        Called log.info('parsed content/feeds/rcos.rst')
        [u'empty', u'rcos']

    '''

    auto_metadata = [('copyright', 'copyright')
                    ]

    auto_pubparts = [('title', 'title')
                    ,('subtitle', 'subtitle')
                    ,('body', 'fragment')
                    ]

    def paths(self):
        '''Return a list of paths to feed objects on the filesystem.

        Consider all the contents of the feeds directory (by default this is
        ``content_root/feeds``).  Only files ending in ``suffix`` are considered.

        Directory entries that are not files are ignored.

            >>> from pysettings.settings import Settings
            >>> s = {'CONTENT_ROOT': 'content'
            ...     ,'FEEDS_SUBDIR': 'feeds'
            ...     ,'REST_EXTENSION': 'rst'
            ...     }
            >>> s = Settings(s)
            >>> f = FeedParser(s)
            >>> f.paths()
            ['content/feeds/empty.rst', 'content/feeds/rcos.rst']

        '''
        # TODO add above settings to global settings.
        settings = self.settings
        path  = os.path.join(settings.CONTENT_ROOT, settings.FEEDS_SUBDIR)
        files = os.listdir(path)
        files = map(lambda p: os.path.join(path, p), files)
        files = filter(lambda f: f.endswith(settings.REST_EXTENSION), files)
        files = filter(lambda f: os.path.isfile(f), files)
        files.sort()
        return files

    def new_object(self, path, d, pub):
        '''Return an instance of the object to which rst documents are parsed.
        '''
        f = RstObject()
        f.slug = unicode(os.path.basename(path).rsplit('.', 1)[0])
        return f

    def default(self, attr):
        '''Return the default value of an attribute.
        '''
        return u''
