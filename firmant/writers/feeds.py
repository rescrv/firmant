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


from copy import copy

from firmant.writers import Writer


class FeedWriter(Writer):
    '''Base class used for functionality common to all feed writers.
    '''


class FeedSingle(FeedWriter):
    '''Parse the posts into single feed documents.
    '''

    fmt = 'atom'

    def path(self, feed):
        '''Use the urlmapper to construct a path for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, type='feed', slug=feed.slug)

    def url(self, feed):
        '''Use the urlmapper to construct a URL for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, absolute=True, type='feed', slug=feed.slug)

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
            ret.append(self.path(feed=feed))
        ret.sort()
        return ret

    def write(self):
        '''Write a parsed feed to the filesystem.

        Example on testdata/pristine::

            >>> fs = FeedSingle(settings, objs, urlmapper)
            >>> fs.write()
            Feed bar
              2010/01/01/newyear
              2009/12/31/party
            Feed baz
              2010/02/02/newday2
              2010/02/02/newday
              2010/02/01/newmonth
            Feed foo
              2010/02/02/newday2
              2010/02/02/newday
              2010/01/01/newyear
            Feed quux
              2010/02/01/newmonth
              2009/12/31/party

        '''
        for feed in self.objs.get('feeds', []):
            feed  = copy(feed)
            posts = [x for x in reversed(sorted(feed.posts,
                    key=lambda p: (p.updated, p.published.date(), p.slug)))]
            feed.posts = posts[:self.settings.POSTS_PER_FEED]
            self.render(feed)

    def render(self, feed):
        '''Render the feed.

        This should be overridden in child classes.
        '''
        print 'Feed %s' % feed.slug
        for post in feed.posts:
            print '  %s/%s' % (post.published.strftime('%Y/%m/%d'), post.slug)


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
                    ,'tags': 'firmant.parsers.tags.TagParser'
                    }
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'FEEDS_SUBDIR': 'feeds'
        ,'TAGS_SUBDIR': 'feeds'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        ,'POSTS_PER_FEED': 3
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
