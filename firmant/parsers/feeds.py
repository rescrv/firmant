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

import pytz

from firmant import decorators
from firmant import parsers


class Feed(parsers.RstParsedObject):
    '''A feed is a means of categorizing objects.

    Attributes of :class:`Feed`:

        slug
           A unique string that identifies the feed.

        title
           A longer title used for identifying the feed to the user.

        subtitle
           An even longer description of the feed that may be displayed to the
           user in combination with `title`.

        copyright
           The copyright of the feed for all posts without an explicit
           copyright.

        content
           The content of the restructured text document.  This does not include
           the title information.

        posts
           A list of cross-referenced posts.  This will be blank until
           cross-referencing happens at a later point in time.

    .. note::

       All string attributes except `slug` may be ``''``.  Posts will be ``[]``
       until the cross-referencing chunk happens.

    .. doctest::

       >>> Feed(slug='foo')
       Feed(foo)

    '''

    # pylint: disable-msg=R0903

    __slots__ = ['slug', 'copyright', 'posts']

    _pubparts = [('content', 'fragment')
                   ,('title', 'title')
                   ,('subtitle', 'subtitle')
                   ]

    def __repr__(self):
        return 'Feed(%s)' % getattr(self, 'slug', None)

    @property
    def _attributes(self):
        '''Attributes that identify a feed object:

            slug
               The `slug` attribute of the :class:`Feed` object.

        .. doctest::

           >>> Feed(slug='foo')._attributes
           {'slug': 'foo'}

        '''
        # pylint: disable-msg=E1101
        return {'slug': self.slug}

    @property
    def updated(self):
        '''Return the update time of the feed.

        If there are no posts, it is 1900-01-01 UTC, otherwise it will be the
        maximum update time across all posts.

        '''
        # pylint: disable-msg=E1101
        return max([post.updated for post in self.posts or []] +
                   [pytz.utc.localize(datetime.datetime(1900, 01, 01))])


class FeedParser(parsers.RstParser):
    r'''Parse all feeds matching ``[-a-zA-Z0-9_]+``.

    .. doctest::
       :hide:

       >>> environment['log'] = get_logger()

    .. doctest::

       >>> fp = FeedParser(environment, objects)
       >>> environment, objects, (parser,) = fp(environment, objects)
       >>> pprint(parser(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {'feed': [Feed(bar), Feed(baz), Feed(foo), Feed(quux)]},
        [])

    '''

    type = 'feed'
    paths = '^[-a-zA-Z0-9_.]+\.rst$'
    cls = Feed

    @decorators.in_environment('settings')
    def root(self, environment):
        '''The directory under which all feed objects reside.
        '''
        settings = environment['settings']
        return os.path.join(settings.CONTENT_ROOT, settings.FEEDS_SUBDIR)

    def rstparse(self, environment, objects, path, pieces):
        '''Use the parsed rst document to construct the necessary objects.
        '''
        attrs = {}
        attrs['slug'] = unicode(path[:-4])
        attrs['copyright'] = pieces['metadata'].get('copyright', '')
        attrs['_pub'] = pieces['pub']
        objects[self.type].append(self.cls(**attrs))


def _setup(test):
    '''Setup the tests.
    '''
    from pysettings.settings import Settings
    from firmant import routing
    test.globs['settings'] = Settings({'CONTENT_ROOT': 'testdata/pristine'
                                      ,'FEEDS_SUBDIR': 'feeds'
                                      })
    urlmapper = routing.URLMapper('/path/to/output/dir', 'http://testurl/', [])
    test.globs['environment'] = {'settings': test.globs['settings']
                                ,'urlmapper': urlmapper
                                }
    test.globs['objects'] = {}
