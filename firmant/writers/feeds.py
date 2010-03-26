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


'''Writers that write various views of the feeds.
'''


from firmant.writers import Writer


class FeedWriter(Writer):
    '''Base class used for functionality common to all feed writers.
    '''


class FeedSingle(FeedWriter):
    '''Parse the posts into single feed documents.
    '''

    fmt = 'atom'

    def url(self, **kwargs):
        '''Use the urlmapper to construct a url for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, type='feed', **kwargs)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

            >>> c = components
            >>> urlmapper.add(c.Type('feed')/c.slug)
            >>> fs = FeedSingle(settings, objs, urlmapper)
            >>> pprint(fs.urls())
            ['bar/index.atom', 'baz/index.atom', 'foo/index.atom', 'quux/index.atom']

        '''
        ret = list()
        for feed in self.objs.get('feeds', []):
            ret.append(self.url(slug=feed.slug))
        ret.sort()
        return ret

    def write(self):
        pass


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
                    }
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'FEEDS_SUBDIR': 'feeds'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    firmant.parse()
    self.globs['settings'] = settings
    self.globs['objs']  = firmant.objs
    self.globs['urlmapper'] = URLMapper()
    self.globs['components'] = components
