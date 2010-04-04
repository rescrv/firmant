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

    def path(self, static):
        '''Use the urlmapper to construct a path for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor('', static=static.relpath)

    def url(self, static):
        '''Use the urlmapper to construct a URL for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor('', absolute=True, static=static.relpath)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

            >>> from firmant import routing
            >>> urlmapper.add(routing.SinglePathComponent('static', str))
            >>> sw = StaticWriter(settings, objs, urlmapper)
            >>> pprint(sw.urls())
            ['images/88x31.png']

        '''
        ret = list()
        for static in self.objs.get('static', []):
            ret.append(self.path(static))
        ret.sort()
        return ret

    def write(self):
        '''Write a parsed feed to the filesystem.
        '''
        for static in self.objs.get('static', []):
            relpath = self.path(static)
            abspath = os.path.join(self.settings.OUTPUT_DIR, relpath)
            try:
                os.makedirs(os.path.dirname(abspath))
            except OSError, e:
                if e.errno != 17:
                    raise
            shutil.copy2(static.fullpath, abspath)


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
    s = {'PARSERS': {'posts': 'firmant.parsers.posts.PostParser'
                    ,'feeds': 'firmant.parsers.feeds.FeedParser'
                    ,'static': 'firmant.parsers.static.StaticParser'
                    ,'tags': 'firmant.parsers.tags.TagParser'
                    }
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'FEEDS_SUBDIR': 'feeds'
        ,'TAGS_SUBDIR': 'feeds'
        ,'STATIC_SUBDIR': 'static'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    from minimock import Mock
    firmant.parse()
    firmant.cross_reference()
    self.globs['settings'] = settings
    self.globs['objs']  = firmant.objs
    self.globs['urlmapper'] = URLMapper()
    self.globs['components'] = components
