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


'''Manipulate tag objects for Firmant.
'''


import os

from firmant.parsers import RstParser
from firmant.parsers import RstObject


__all__ = ['TagParser']


class TagParser(RstParser):
    r'''Interpret *.rst for a given tag directory.

    For each reSt document, parse it to a tag and extract its metadata.

        >>> t = TagParser()
        >>> t = t.parse_one('content/tags/rcos.rst')
        >>> t.slug
        u'rcos'
        >>> t.title
        u'Rensselaer Center for Open Source'
        >>> t.subtitle
        u'Helping to make the world a better place:  One project at a time'
        >>> t.copyright
        u'This document is public domain'
        >>> t.body
        u'<p>The body of the tag document.</p>\n'

    Default values (except slug)::

        >>> # Test the empty-file case.
        >>> t = TagParser()
        >>> t = t.parse_one('content/tags/empty.rst')
        >>> t.slug
        u'empty'
        >>> t.title
        u''
        >>> t.subtitle
        u''
        >>> t.copyright
        u''
        >>> t.body
        u''

    Note that posts are not cross-referenced at this point.  This also implies
    that the update time is not set::

        >>> t.posts
        Traceback (most recent call last):
        AttributeError: 'RstObject' object has no attribute 'posts'
        >>> t.updated
        Traceback (most recent call last):
        AttributeError: 'RstObject' object has no attribute 'updated'

    All tags may be retrieved with::

        >>> from pysettings.settings import Settings
        >>> s = {'CONTENT_ROOT': 'content'
        ...     ,'TAGS_SUBDIR': 'tags'
        ...     ,'REST_EXTENSION': 'rst'
        ...     }
        >>> s = Settings(s)
        >>> t = TagParser(s)
        >>> t.log = Mock('log')
        >>> map(lambda t: t.slug, t.parse())
        Called log.info('parsed content/tags/empty.rst')
        Called log.info('parsed content/tags/rcos.rst')
        [u'empty', u'rcos']

    '''

    auto_metadata = [('copyright', 'copyright')
                    ]

    auto_pubparts = [('title', 'title')
                    ,('subtitle', 'subtitle')
                    ,('body', 'fragment')
                    ]

    def paths(self):
        '''Return a list of paths to tag objects on the filesystem.

        Consider all the contents of the tags directory (by default this is
        ``content_root/tags``).  Only files ending in ``suffix`` are considered.

        Directory entries that are not files are ignored.

            >>> from pysettings.settings import Settings
            >>> s = {'CONTENT_ROOT': 'content'
            ...     ,'TAGS_SUBDIR': 'tags'
            ...     ,'REST_EXTENSION': 'rst'
            ...     }
            >>> s = Settings(s)
            >>> t = TagParser(s)
            >>> t.paths()
            ['content/tags/empty.rst', 'content/tags/rcos.rst']

        '''
        # TODO add above settings to global settings.
        settings = self.settings
        path  = os.path.join(settings.CONTENT_ROOT, settings.TAGS_SUBDIR)
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
