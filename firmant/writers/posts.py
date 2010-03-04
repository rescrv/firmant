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

from firmant import paginate
from firmant.writers import Writer


class PostArchiveBase(Writer):
    '''Parse the posts into lists of size POSTS_PER_PAGE.

    When instantiating, if the setting for ``POSTS_PER_PAGE`` is not a
    positive, non-zero integer, it will raise a value error::

        >>> from pysettings.settings import Settings
        >>> PostArchiveAll(Settings(POSTS_PER_PAGE=0), [])
        Traceback (most recent call last):
        ValueError: POSTS_PER_PAGE must be a positive value.

    '''

    def __init__(self, settings, objs):
        Writer.__init__(self, settings, objs)
        if settings.POSTS_PER_PAGE < 1:
            raise ValueError('POSTS_PER_PAGE must be a positive value.')

    def for_split_posts(self, key, action):
        per_page = self.settings.POSTS_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        split_lists = paginate.split_boundary(key, posts)
        for key, split_list in split_lists:
            split_posts = paginate.paginate(per_page, split_list)
            for page, num_pages, begin, end, posts in split_posts:
                action(key, page, num_pages, begin, end, posts)


class PostArchiveAll(PostArchiveBase):
    '''Parse the posts into a list, grouped by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> paa = PostArchiveAll(settings, firmant.objs)
        >>> from pprint import pprint
        >>> pprint(paa.urls())
        ['/index.html', '/page2.html', '/page3.html']

        '''
        per_page = self.settings.POSTS_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        split_posts = paginate.paginate(per_page, posts)

        ret = list()
        for page, num_pages, begin, end, posts in split_posts:
            if page == 1:
                ret.append('/index.html')
            else:
                ret.append('/page%i.html' % page)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> paa = PostArchiveAll(settings, firmant.objs)
        >>> paa.write()
        Page 1 1-2 of 3:
          - 2010-02-02-newday2
          - 2010-02-02-newday
        Page 2 3-4 of 3:
          - 2010-02-01-newmonth
          - 2010-01-01-newyear
        Page 3 5-5 of 3:
          - 2009-12-31-party

        '''
        per_page = self.settings.POSTS_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        split_posts = paginate.paginate(per_page, posts)

        for page, num_pages, begin, end, posts in split_posts:
            self.render(page, num_pages, begin, end, posts)

    def render(self, page, num_pages, first, last, posts):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Page %i %i-%i of %i:' % (page, first, last, num_pages)
        for post in posts:
            s = post.published.strftime('  - %Y-%m-%d-%%s')
            print s % post.slug


class PostArchiveYearly(PostArchiveBase):
    '''Parse the posts into a list, grouped by year, then by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> pay = PostArchiveYearly(settings, firmant.objs)
        >>> from pprint import pprint
        >>> pprint(pay.urls())
        ['/2010/index.html', '/2010/page2.html', '/2009/index.html']

        '''
        per_page = self.settings.POSTS_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        def key(x):
            if x is None:
                return None
            return x.published.year

        ret = list()
        split_lists = paginate.split_boundary(key, posts)
        for year, split_list in split_lists:
            split_posts = paginate.paginate(per_page, split_list)
            for page, num_pages, begin, end, posts in split_posts:
                if page == 1:
                    ret.append('/%04i/index.html' % year)
                else:
                    ret.append('/%04i/page%i.html' % (year, page))
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> pay = PostArchiveYearly(settings, firmant.objs)
        >>> pay.write()
        Year 2010:
            Page 1 1-2 of 2:
              - 2010-02-02-newday2
              - 2010-02-02-newday
        Year 2010:
            Page 2 3-4 of 2:
              - 2010-02-01-newmonth
              - 2010-01-01-newyear
        Year 2009:
            Page 1 1-1 of 1:
              - 2009-12-31-party

        '''
        per_page = self.settings.POSTS_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        def key(x):
            if x is None:
                return None
            return x.published.year

        split_lists = paginate.split_boundary(key, posts)
        for year, split_list in split_lists:
            split_posts = paginate.paginate(per_page, split_list)
            for page, num_pages, begin, end, posts in split_posts:
                self.render(year, page, num_pages, begin, end, posts)

    def render(self, year, page, num_pages, first, last, posts):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Year %04i:' % year
        print '    Page %i %i-%i of %i:' % (page, first, last, num_pages)
        for post in posts:
            s = post.published.strftime('      - %Y-%m-%d-%%s')
            print s % post.slug


class PostArchiveMonthly(PostArchiveBase):
    '''Parse the posts into a list, grouped by month, then by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> pam = PostArchiveMonthly(settings, firmant.objs)
        >>> from pprint import pprint
        >>> pprint(pam.urls())
        ['/2010/02/index.html',
         '/2010/02/page2.html',
         '/2010/01/index.html',
         '/2009/12/index.html']

        '''
        ret = list()
        def key(x):
            if x is None:
                return None
            return (x.published.year, x.published.month)
        def action(month, page, num_pages, first, last, posts):
            if page == 1:
                ret.append('/%04i/%02i/index.html' % month)
            else:
                ret.append('/%04i/%02i/page%i.html' % (month + (page,)))
        self.for_split_posts(key, action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> pam = PostArchiveMonthly(settings, firmant.objs)
        >>> pam.write()
        Month 2010-02:
            Page 1 1-2 of 2:
              - 2010-02-02-newday2
              - 2010-02-02-newday
        Month 2010-02:
            Page 2 3-3 of 2:
              - 2010-02-01-newmonth
        Month 2010-01:
            Page 1 1-1 of 1:
              - 2010-01-01-newyear
        Month 2009-12:
            Page 1 1-1 of 1:
              - 2009-12-31-party

        '''
        def key(x):
            if x is None:
                return None
            return (x.published.year, x.published.month)
        self.for_split_posts(key, self.render)

    def render(self, month, page, num_pages, first, last, posts):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Month %04i-%02i:' % month
        print '    Page %i %i-%i of %i:' % (page, first, last, num_pages)
        for post in posts:
            s = post.published.strftime('      - %Y-%m-%d-%%s')
            print s % post.slug


class PostArchiveDaily(PostArchiveBase):
    '''Parse the posts into a list, grouped by day, then by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> settings.POSTS_PER_PAGE = 1
        >>> pad = PostArchiveDaily(settings, firmant.objs)
        >>> from pprint import pprint
        >>> pprint(pad.urls())
        ['/2010/02/02/index.html',
         '/2010/02/02/page2.html',
         '/2010/02/01/index.html',
         '/2010/01/01/index.html',
         '/2009/12/31/index.html']

        '''
        ret = list()
        def key(x):
            if x is None:
                return None
            return (x.published.year, x.published.month, x.published.day)
        def action(day, page, num_pages, first, last, posts):
            if page == 1:
                ret.append('/%04i/%02i/%02i/index.html' % day)
            else:
                ret.append('/%04i/%02i/%02i/page%i.html' % (day + (page,)))
        self.for_split_posts(key, action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> settings.POSTS_PER_PAGE = 1
        >>> pad = PostArchiveDaily(settings, firmant.objs)
        >>> pad.write()
        Day 2010-02-02:
            Page 1 1-1 of 2:
              - 2010-02-02-newday2
        Day 2010-02-02:
            Page 2 2-2 of 2:
              - 2010-02-02-newday
        Day 2010-02-01:
            Page 1 1-1 of 1:
              - 2010-02-01-newmonth
        Day 2010-01-01:
            Page 1 1-1 of 1:
              - 2010-01-01-newyear
        Day 2009-12-31:
            Page 1 1-1 of 1:
              - 2009-12-31-party

        '''
        def key(x):
            if x is None:
                return None
            return (x.published.year, x.published.month, x.published.day)
        self.for_split_posts(key, self.render)

    def render(self, day, page, num_pages, first, last, posts):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Day %04i-%02i-%02i:' % day
        print '    Page %i %i-%i of %i:' % (page, first, last, num_pages)
        for post in posts:
            s = post.published.strftime('      - %Y-%m-%d-%%s')
            print s % post.slug


def _setUp(self):
    from pysettings.settings import Settings
    from firmant.application import Firmant
    s = {'PARSERS': {'posts': 'firmant.parsers.posts.PostParser'}
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    firmant.parse()
    self.globs['settings'] = settings
    self.globs['firmant']  = firmant
