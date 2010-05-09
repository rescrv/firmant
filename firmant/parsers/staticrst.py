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


'''StaticRst objects (also known as "flatpages")  provide for free-form page
layouts.
'''


import os

from firmant.parsers import RstObject
from firmant.parsers import RstParser
from firmant.utils import paths


class StaticRstParser(RstParser):
    '''Create a static page from reStructured Text.

    For each reSt document, parse it to a page and extract its metadata.

        >>> p = StaticRstParser(settings)
        >>> p = p.parse_one('content/flat/links.rst')
        >>> p.copyright
        u'This document is part of the public domain.'
        >>> p.title
        u'Links'
        >>> p.content #doctest: +ELLIPSIS
        u'<ul class="simple">...</ul>\\n'

    Default values::

        >>> p = StaticRstParser(settings)
        >>> p = p.parse_one('content/flat/empty.rst')
        >>> p.title
        u''
        >>> p.content #doctest: +ELLIPSIS
        u''

    All static pages may be retrieved with::

        >>> p = StaticRstParser(settings)
        >>> p.log = Mock('log')
        >>> pprint(map(lambda p: p.title, p.parse()))
        Called log.info('parsed content/flat/about.rst')
        Called log.info('parsed content/flat/empty.rst')
        Called log.info('parsed content/flat/links.rst')
        [u'About', u'', u'Links']

    '''

    auto_metadata = [('copyright', 'copyright')]

    auto_pubparts = [('title', 'title')
                    ,('content', 'fragment')
                    ]

    def paths(self):
        '''A list of files to parse.

        .. doctest::
           :hide:

           >>> srp = StaticRstParser(settings)

        .. doctest::

           >>> pprint(srp.paths())
           ['content/flat/about.rst', 'content/flat/empty.rst', 'content/flat/links.rst']

        '''
        path = self.root_path({'settings': self.settings})
        return sorted(paths.recursive_listdir(path, matches='.*\.rst'))

    def new_object(self, path, d, pub):
        '''Return an instance of the object to which rst documents are parsed.
        '''
        settings = self.settings
        root = os.path.join(settings.CONTENT_ROOT, settings.STATIC_RST_SUBDIR)
        if path.startswith(root):
            path = path[len(root):]
        if path.startswith('/'):
            path = path[1:]
        p = RstObject()
        p.path = unicode(path.rsplit('.', 1)[0])
        return p

    def default(self, attr):
        '''Return the default value of an attribute.
        '''
        d = {}
        return d.get(attr, u'')

    @staticmethod
    def root_path(environment):
        '''The directory under which all static objects reside.
        '''
        settings = environment['settings']
        return os.path.join(settings.CONTENT_ROOT, settings.STATIC_RST_SUBDIR)


def _setup(test):
    from pysettings.settings import Settings
    test.globs['settings'] = Settings({'CONTENT_ROOT': 'content'
                                      ,'STATIC_RST_SUBDIR': 'flat'
                                      ,'REST_EXTENSION': 'rst'
                                      })
