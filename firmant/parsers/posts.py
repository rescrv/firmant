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

import pytz

from firmant import decorators
from firmant import parsers
from firmant.utils import strptime


class Post(parsers.RstParsedObject):
    '''A post is piece of content identified by a date of publication and a
    slug.

    Attributes of :class:`Post`:

        slug
           A unique string that identifies the post.

        published
           The date and time of publication of the post.

        title
           A longer title used for identifying the post to the user.

        author
           The person who authored the post.

        copyright
           The copyright of the post.  Absence of a copyright implies all rights
           are reserved (except in the case that a post without a copyright
           belongs to a feed with a copyright).

        content
           The content of the restructured text document.  This does not include
           the title information.

        updated
           The time at which the post was last updated (defaults to the time of
           publication).

        tags
           A list of cross-referenced tags.  This will contain only slugs until
           cross-referencing happens at a later point in time.

        feeds
           A list of cross-referenced feeds.  This will contain only slugs until
           cross-referencing happens at a later point in time.

    .. note::

       All string attributes except `slug` may be ``''``.  Posts will be ``[]``
       until the cross-referencing chunk happens.

    .. doctest::

       >>> from pytz import utc
       >>> from datetime import datetime
       >>> Post(published=utc.localize(datetime(2010, 1, 1)), slug='foopost')
       Post(2010-01-01-foopost)

    '''

    # pylint: disable-msg=R0903

    __slots__ = ['slug', 'published', 'author', 'copyright',
            'updated', 'tags', 'feeds']

    _pubparts = [('content', 'fragment')
                   ,('title', 'title')
                   ]

    def __repr__(self):
        dt = getattr(self, 'published', None)
        if dt is not None:
            dt = dt.strftime('%Y-%m-%d')
        return 'Post(%s-%s)' % (dt, getattr(self, 'slug', None))

    @property
    def _attributes(self):
        '''Attributes that identify a post object:

            year
               The year of publication.

            month
               The month of publication.

            day
               The day of publication.

            slug
               The `slug` attribute of the :class:`Post` object.

        .. doctest::

           >>> from datetime import datetime
           >>> pprint(Post(published=datetime(2009, 12, 31), slug='party')._attributes)
           {'day': 31, 'month': 12, 'slug': 'party', 'year': 2009}

        '''
        # pylint: disable-msg=E1101
        return {'year': self.published.year
               ,'month': self.published.month
               ,'day': self.published.day
               ,'slug': self.slug
               }


class PostParser(parsers.RstParser):
    '''Parse all posts matching ``[0-9]{4}-[0-9]{2}-[0-9]{2}-[-a-zA-Z0-9_]+``.

    .. doctest::
       :hide:

       >>> environment['log'] = get_logger()

    .. doctest::

       >>> pp = PostParser(environment, objects)
       >>> environment, objects, (parser,) = pp(environment, objects)
       >>> pprint(parser(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {'post': [Post(2009-12-31-party),
                  Post(2010-01-01-newyear),
                  Post(2010-02-01-newmonth),
                  Post(2010-02-02-newday),
                  Post(2010-02-02-newday2)]},
        [])

    '''

    type = 'post'
    paths = '^[0-9]{4}-[0-9]{2}-[0-9]{2}-[-a-zA-Z0-9_]+\.rst$'
    cls = Post

    @decorators.in_environment('settings')
    def root(self, environment):
        '''The directory under which all post objects reside.
        '''
        settings = environment['settings']
        return os.path.join(settings.CONTENT_ROOT, settings.POSTS_SUBDIR)

    def rstparse(self, environment, objects, path, pieces):
        '''Use the parsed rst document to construct the necessary objects.
        '''
        timezone = pytz.timezone(pieces['metadata'].get('timezone', 'UTC'))
        # Set times
        time = pieces['metadata'].get('time', datetime.time(0, 0, 0))
        pubdate = strptime(os.path.basename(path)[:10], ['%Y-%m-%d'])
        published = datetime.datetime.combine(pubdate.date(), time)
        updated = pieces['metadata'].get('updated', published)
        # Other attrs
        attrs = {}
        attrs['slug'] = unicode(path[11:-4])
        attrs['author'] = pieces['metadata'].get('author', '')
        attrs['copyright'] = pieces['metadata'].get('copyright', '')
        attrs['tags'] = pieces['metadata'].get('tags', [])
        attrs['feeds'] = pieces['metadata'].get('feeds', [])
        attrs['published'] = timezone.localize(published)
        attrs['updated'] = timezone.localize(updated)
        attrs['_pub'] = pieces['pub']
        objects[self.type].append(self.cls(**attrs))


def _setup(test):
    '''Setup the tests.
    '''
    from pysettings.settings import Settings
    from firmant import routing
    test.globs['settings'] = Settings({'CONTENT_ROOT': 'testdata/pristine'
                                      ,'POSTS_SUBDIR': 'posts'
                                      })
    urlmapper = routing.URLMapper('/path/to/output/dir', 'http://testurl/', [])
    test.globs['environment'] = {'settings': test.globs['settings']
                                ,'urlmapper': urlmapper
                                }
    test.globs['objects'] = {}
