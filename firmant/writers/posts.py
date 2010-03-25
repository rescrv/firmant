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
from firmant.i18n import _
from firmant.writers import Writer


class PostArchiveBase(Writer):
    '''Parse the posts into lists of size POSTS_PER_PAGE.
    '''

    def for_split_posts(self, key, action):
        '''For each group, for each page in the group, call action.

        Action will be provided with the page, the total number of pages, the
        beginning and ending indices (1-indexed) of the posts, and the posts
        themselves.  It will also get the elements of the key.
        '''
        per_page = self.settings.POSTS_PER_PAGE

        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published.date(), p.slug), reverse=True)

        split_lists = paginate.split_boundary(key, posts)
        for key, split_list in split_lists:
            split_posts = paginate.paginate(per_page, split_list)
            for page, num_pages, begin, end, posts in split_posts:
                action(page, num_pages, begin, end, posts, *key)

    def write_preconditions(self):
        '''Returns true if and only if it is acceptable to proceed with writing.

        It is a precondition for writing that ``POSTS_PER_PAGE`` be set to a
        positive, non-zero integer.

            >>> from pysettings.settings import Settings
            >>> paa = PostArchiveAll(Settings(POSTS_PER_PAGE=0), {}, None)
            >>> paa.log = Mock('log')
            >>> paa.write_preconditions()
            Called log.critical('``POSTS_PER_PAGE`` must be a positive int.')
            False

        It is another precondition for writing that there be posts in the parsed
        objects dictionary::

            >>> from pysettings.settings import Settings
            >>> paa = PostArchiveAll(Settings(POSTS_PER_PAGE=1), {}, None)
            >>> paa.log = Mock('log')
            >>> paa.write_preconditions()
            Called log.critical('``posts`` must be in parsed objects.')
            False

        '''
        # Fail if we do not have an output directory.
        if getattr(self.settings, 'POSTS_PER_PAGE', -1) < 1:
            self.log.critical(_('``POSTS_PER_PAGE`` must be a positive int.'))
            return False
        if 'posts' not in self.objs:
            self.log.critical(_('``posts`` must be in parsed objects.'))
            return False
        return super(PostArchiveBase, self).write_preconditions()

    def url(self, **kwargs):
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, type='post', **kwargs)


class PostArchiveAll(PostArchiveBase):
    '''Parse the posts into a list, grouped by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    fmt = 'html'

    def key(self, post):
        '''The key for a post is a constant zero-tuple.
        '''
        if post is None:
            return None
        return ()

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> urlmapper.add(components.Type('post')/components.pageno)
        >>> paa = PostArchiveAll(settings, objs, urlmapper)
        >>> pprint(paa.urls())
        ['index.html', 'page2/index.html', 'page3/index.html']

        '''
        ret = list()
        def action(page, num_pages, first, last, posts):
            ret.append(self.url(page=page))
        self.for_split_posts(self.key, action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> paa = PostArchiveAll(settings, objs, urlmapper)
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
        self.for_split_posts(self.key, self.render)

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

    fmt = 'html'

    def key(self, post):
        '''Posts are keyed by year.
        '''
        if post is None:
            return None
        return (post.published.year,)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> urlmapper.add(components.Type('post')/components.year/components.pageno)
        >>> pay = PostArchiveYearly(settings, objs, urlmapper)
        >>> pprint(pay.urls())
        ['2010/index.html', '2010/page2/index.html', '2009/index.html']

        '''
        ret = list()
        def action(page, num_pages, first, last, posts, year):
            ret.append(self.url(page=page, year=year))
        self.for_split_posts(self.key, action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> pay = PostArchiveYearly(settings, objs, urlmapper)
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
        self.for_split_posts(self.key, self.render)

    def render(self, page, num_pages, first, last, posts, year):
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

    fmt = 'html'

    def key(self, post):
        '''Posts are keyed by month.
        '''
        if post is None:
            return None
        return (post.published.year, post.published.month)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> urlmapper.add(
        ...     components.Type('post')/components.year/components.month/components.pageno)
        >>> pam = PostArchiveMonthly(settings, objs, urlmapper)
        >>> pprint(pam.urls())
        ['2010/02/index.html',
         '2010/02/page2/index.html',
         '2010/01/index.html',
         '2009/12/index.html']

        '''
        ret = list()
        def action(page, num_pages, first, last, posts, year, month):
            ret.append(self.url(page=page, year=year, month=month))
        self.for_split_posts(self.key, action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> pam = PostArchiveMonthly(settings, objs, urlmapper)
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
        self.for_split_posts(self.key, self.render)

    def render(self, page, num_pages, first, last, posts, year, month):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Month %04i-%02i:' % (year, month)
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

    fmt = 'html'

    def key(self, post):
        '''Posts are keyed by day.
        '''
        if post is None:
            return None
        return (post.published.year, post.published.month, post.published.day)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> c = components
        >>> settings.POSTS_PER_PAGE = 1
        >>> urlmapper.add(
        ...     c.Type('post')/c.year/c.month/c.day/c.pageno)
        >>> pad = PostArchiveDaily(settings, objs, urlmapper)
        >>> pprint(pad.urls())
        ['2010/02/02/index.html',
         '2010/02/02/page2/index.html',
         '2010/02/01/index.html',
         '2010/01/01/index.html',
         '2009/12/31/index.html']

        '''
        ret = list()
        def action(page, num_pages, first, last, posts, year, month, day):
            ret.append(self.url(page=page, year=year, month=month, day=day))
        self.for_split_posts(self.key, action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> settings.POSTS_PER_PAGE = 1
        >>> pad = PostArchiveDaily(settings, objs, urlmapper)
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
        self.for_split_posts(self.key, self.render)

    def render(self, page, num_pages, first, last, posts, year, month, day):
        '''Render the function.

        This should be overridden in base classes.
        '''
        print 'Day %04i-%02i-%02i:' % (year, month, day)
        print '    Page %i %i-%i of %i:' % (page, first, last, num_pages)
        for post in posts:
            s = post.published.strftime('      - %Y-%m-%d-%%s')
            print s % post.slug


class PostSingle(Writer):
    '''Parse the posts into single pages.
    '''

    fmt = 'html'

    def url(self, **kwargs):
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, type='post', **kwargs)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

            >>> c = components
            >>> urlmapper.add(c.Type('post')/c.year/c.month/c.day/c.slug)
            >>> ps = PostSingle(settings, objs, urlmapper)
            >>> pprint(ps.urls())
            ['2009/12/31/party/index.html',
             '2010/01/01/newyear/index.html',
             '2010/02/01/newmonth/index.html',
             '2010/02/02/newday/index.html',
             '2010/02/02/newday2/index.html']

        '''
        ret = list()
        for post in self.objs['posts']:
            ret.append(self.url(year=post.published.year,
                month=post.published.month, day=post.published.day,
                slug=post.slug))
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> ps = PostSingle(settings, objs, urlmapper)
        >>> ps.write()
        Post 2009/12/31/party
        Post 2010/01/01/newyear
        Post 2010/02/01/newmonth
        Post 2010/02/02/newday
        Post 2010/02/02/newday2

        '''
        for post in self.objs['posts']:
            self.render(post)

    def render(self, post):
        '''Render the posts.

        This should be overridden in child classes.
        '''
        print 'Post %s/%s' % (post.published.strftime('%Y/%m/%d'), post.slug)


def _setup(self):
    from pysettings.settings import Settings
    from firmant.application import Firmant
    from firmant.routing import URLMapper
    from firmant.routing import components
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
    self.globs['objs']  = firmant.objs
    self.globs['urlmapper'] = URLMapper()
    self.globs['components'] = components
