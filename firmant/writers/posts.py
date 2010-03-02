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


from copy import copy

from firmant.paginate import paginate
from firmant.writers import Writer


class PostArchiveAll(Writer):
    '''Parse the posts into a list, grouped by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    When instantiating, if the setting for ``ENTRIES_PER_PAGE`` is not a
    positive, non-zero integer, it will raise a value error::

        >>> from pysettings.settings import Settings
        >>> PostArchiveAll(Settings(ENTRIES_PER_PAGE=0), [])
        Traceback (most recent call last):
        ValueError: ENTRIES_PER_PAGE must be a positive value.

    '''

    def __init__(self, settings, objs):
        Writer.__init__(self, settings, objs)
        if settings.ENTRIES_PER_PAGE < 1:
            raise ValueError('ENTRIES_PER_PAGE must be a positive value.')

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> from pysettings.settings import Settings
        >>> from firmant.application import Firmant
        >>> s = {'PARSERS': {'posts': 'firmant.parsers.posts.PostParser'}
        ...     ,'CONTENT_ROOT': 'testdata/pristine'
        ...     ,'POSTS_SUBDIR': 'posts'
        ...     ,'REST_EXTENSION': 'rst'
        ...     ,'ENTRIES_PER_PAGE': 2
        ...     }
        >>> s = Settings(s)
        >>> f = Firmant(s)
        >>> f.parse()
        >>> eaa = PostArchiveAll(s, f.objs)
        >>> eaa.write()
        Page 1 1-2 of 3:
          - 2010-02-02-newday2
          - 2010-02-02-newday
        Page 2 3-4 of 3:
          - 2010-02-01-newmonth
          - 2010-01-01-newyear
        Page 3 5-5 of 3:
          - 2009-12-31-party

        '''
        per_page = self.settings.ENTRIES_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        for page, num_pages, begin, end, posts in paginate(per_page, posts):
            self.render(page, num_pages, begin, end, posts)

    def render(self, page, num_pages, first, last, posts):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Page %i %i-%i of %i:' % (page, first, last, num_pages)
        for post in posts:
            s = post.published.strftime('  - %Y-%m-%d-%%s')
            print s % post.slug
