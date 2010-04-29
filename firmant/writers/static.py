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


'''Copy static objects into their proper place in the output.
'''


import os
import shutil

from firmant.writers import Writer


class StaticWriter(Writer):
    '''Parse the posts into single feed documents.
    '''

    permalinks_for = 'static'

    def url(self, static):
        '''Use the urlmapper to construct a URL for the given attributes.
        '''
        return self.urlmapper.url(None, static=static.relpath)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

            >>> from firmant import routing
            >>> urlmapper.add(routing.SinglePathComponent('static', str))
            >>> sw = StaticWriter(settings, objs, urlmapper)
            >>> pprint(sw.urls())
            ['http://test/images/88x31.png']

        '''
        ret = list()
        for static in self.objs.get('static', []):
            ret.append(self.url(static))
        ret.sort()
        return ret

    def write(self):
        '''Write a parsed feed to the filesystem.
        '''
        for static in self.objs.get('static', []):
            relpath = self.urlmapper.path(None, static=static.relpath)
            abspath = os.path.join(self.settings.OUTPUT_DIR, relpath)
            try:
                os.makedirs(os.path.dirname(abspath))
            except OSError, e:
                if e.errno != 17:
                    raise
            shutil.copy2(static.fullpath, abspath)


class StaticRstWriter(Writer):
    '''Parse the posts into single feed documents.
    '''

    fmt = 'html'

    def url(self, static):
        '''Use the urlmapper to construct a URL for the given attributes.
        '''
        return self.urlmapper.url(self.fmt, type='staticrst', path=static.path)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

            >>> from firmant import routing
            >>> c = components
            >>> urlmapper.add(c.TYPE('staticrst')/c.PATH)
            >>> srw = StaticRstWriter(settings, objs, urlmapper)
            >>> pprint(srw.urls())
            ['http://test/about/', 'http://test/empty/', 'http://test/links/']

        '''
        ret = list()
        for static in self.objs.get('staticrst', []):
            ret.append(self.url(static))
        ret.sort()
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

            >>> srw = StaticRstWriter(settings, objs, urlmapper)
            >>> srw.write() #doctest: +ELLIPSIS
            Static page  --- 
            Static page About --- <p>Firmant is...</p>
            <BLANKLINE>
            Static page Links --- <ul class="simple">
            <li>...</li>
            <li>...</li>
            </ul>
            <BLANKLINE>

        '''
        pages = self.objs['staticrst']
        pages.sort(key=lambda s: s.title)
        for page in pages:
            self.render(page)

    def render(self, static):
        '''Render the static page.

        This should be overridden in child classes.
        '''
        print 'Static page %s --- %s' % (static.title, static.content)


def _setup(self):
    '''Setup the test cases.

    Actions taken::

        - Create a ``Settings`` object.
        - Create a ``Firmant`` object.
        - Load modules used in tests.

    '''
    from pysettings.settings import Settings
    from firmant.application import Firmant
    from firmant.routing import URLMapper
    from firmant.routing import components
    s = {'PARSERS': {'static': 'firmant.parsers.static.StaticParser'
                    ,'staticrst': 'firmant.parsers.static.StaticRstParser'
                    }
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'OUTPUT_DIR': 'outputdir'
        ,'PERMALINK_ROOT': 'http://urlroot'
        ,'STATIC_SUBDIR': 'static'
        ,'STATIC_RST_SUBDIR': 'flat'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        ,'PERMALINK_ROOT': 'http://test'
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    from minimock import Mock
    firmant.parse()
    firmant.cross_reference()
    self.globs['settings'] = settings
    self.globs['objs']  = firmant.objs
    self.globs['urlmapper'] = URLMapper(settings.OUTPUT_DIR,
            settings.PERMALINK_ROOT)
    self.globs['components'] = components
