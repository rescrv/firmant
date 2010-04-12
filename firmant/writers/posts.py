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


'''Writers that write various views of the posts.
'''


from copy import copy

from firmant import paginate
from firmant.i18n import _
from firmant.writers import Writer


class PostWriter(Writer):
    '''Base class used for functionality common to all post writers.
    '''

    def _sorted_posts(self):
        '''Return the posts sorted by (date, slug)
        '''
        posts = copy(self.objs['posts'])
        posts.sort(key=lambda p: (p.published, p.slug), reverse=True)
        return posts


class PostArchiveBase(PostWriter):
    '''Parse the posts into lists of size POSTS_PER_PAGE.
    '''

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

    def path(self, **kwargs):
        '''Use the urlmapper to construct a path for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, type='post', **kwargs)


class PostArchiveAll(PostArchiveBase):
    '''Parse the posts into a list, grouped by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    fmt = 'html'

    def rev_key(self, key):
        '''Return a dictionary mapping attributes to values in the key.
        '''
        return {}

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> urlmapper.add(components.Type('post')/components.pageno)
        >>> paa = PostArchiveAll(settings, objs, urlmapper)
        >>> pprint(paa.urls())
        ['index.html', 'page2/index.html', 'page3/index.html']

        '''
        ret = list()
        def action(post_list, pages):
            '''The action to pass to paginate_action.
            '''
            ret.append(self.path(page=pages.cur))
        paginate.paginate_action(self.settings.POSTS_PER_PAGE,
                self._sorted_posts(), action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> paa = PostArchiveAll(settings, objs, urlmapper)
        >>> paa.write()
        No previous page.
        Index 1
        Next 2
          - 2010-02-02-newday2
          - 2010-02-02-newday
        Prev 1
        Index 2
        Next 3
          - 2010-02-01-newmonth
          - 2010-01-01-newyear
        Prev 2
        Index 3
        No next page.
          - 2009-12-31-party

        '''
        paginate.paginate_action(self.settings.POSTS_PER_PAGE,
                self._sorted_posts(), self.render)

    def render(self, posts, pages):
        '''Render the view

        This should be overridden in child classes.
        '''
        if pages.prev is None:
            print 'No previous page.'
        else:
            print 'Prev', pages.prev
        print 'Index', pages.cur
        if pages.next is None:
            print 'No next page.'
        else:
            print 'Next', pages.next
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
        '''The key for the post.
        '''
        return (post.published.year,)

    def rev_key(self, key):
        '''Return a dictionary mapping attributes to values in the key.
        '''
        return {'year': key[0]}

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

        >>> urlmapper.add(components.Type('post')/components.year/components.pageno)
        >>> pay = PostArchiveYearly(settings, objs, urlmapper)
        >>> pprint(pay.urls())
        ['2010/index.html', '2010/page2/index.html', '2009/index.html']

        '''
        ret = list()
        def action(obj_list, years, pages):
            '''The action to pass to split_paginate_action.
            '''
            ret.append(self.path(page=pages.cur, year=years.cur[0]))
        paginate.split_paginate_action(self.settings.POSTS_PER_PAGE,
                self.key, self._sorted_posts(), action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> pay = PostArchiveYearly(settings, objs, urlmapper)
        >>> pay.write()
        No previous year.
        Current year: 2010
        Next year: 2009
            No previous page.
            Index 1
            Next 2
             - 2010-02-02-newday2
             - 2010-02-02-newday
        No previous year.
        Current year: 2010
        Next year: 2009
            Prev 1
            Index 2
            No next page.
             - 2010-02-01-newmonth
             - 2010-01-01-newyear
        Previous year: 2010
        Current year: 2009
        No next year.
            No previous page.
            Index 1
            No next page.
             - 2009-12-31-party

        '''
        paginate.split_paginate_action(self.settings.POSTS_PER_PAGE,
                self.key, self._sorted_posts(), self.render)

    def render(self, posts, years, pages):
        '''Render the page corresponding to a single year/page.

        This should be overridden in child classes.
        '''
        if years.prev is None:
            print 'No previous year.'
        else:
            print 'Previous year: %s' % years.prev[0]
        print 'Current year: %s' % years.cur[0]
        if years.next is None:
            print 'No next year.'
        else:
            print 'Next year: %s' % years.next[0]

        if pages.prev is None:
            print '    No previous page.'
        else:
            print '    Prev', pages.prev
        print '    Index', pages.cur
        if pages.next is None:
            print '    No next page.'
        else:
            print '    Next', pages.next
        for post in posts:
            s = post.published.strftime('     - %Y-%m-%d-%%s')
            print s % post.slug


class PostArchiveMonthly(PostArchiveBase):
    '''Parse the posts into a list, grouped by month, then by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    fmt = 'html'

    def key(self, post):
        '''The key for the post.
        '''
        return (post.published.year, post.published.month)

    def rev_key(self, key):
        '''Return a dictionary mapping attributes to values in the key.
        '''
        return {'year': key[0], 'month': key[1]}

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
        def action(obj_list, months, pages):
            '''The action to pass to split_paginate_action.
            '''
            ret.append(self.path(page=pages.cur, year=months.cur[0],
                month=months.cur[1]))
        paginate.split_paginate_action(self.settings.POSTS_PER_PAGE,
                self.key, self._sorted_posts(), action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> pam = PostArchiveMonthly(settings, objs, urlmapper)
        >>> pam.write()
        No previous month.
        Current month: 2010-2
        Next month: 2010-1
            No previous page.
            Index 1
            Next 2
             - 2010-02-02-newday2
             - 2010-02-02-newday
        No previous month.
        Current month: 2010-2
        Next month: 2010-1
            Prev 1
            Index 2
            No next page.
             - 2010-02-01-newmonth
        Previous month: 2010-2
        Current month: 2010-1
        Next month: 2009-12
            No previous page.
            Index 1
            No next page.
             - 2010-01-01-newyear
        Previous month: 2010-1
        Current month: 2009-12
        No next month.
            No previous page.
            Index 1
            No next page.
             - 2009-12-31-party

        '''
        paginate.split_paginate_action(self.settings.POSTS_PER_PAGE,
                self.key, self._sorted_posts(), self.render)

    def render(self, posts, months, pages):
        '''Render the page corresponding to a single month/page.

        This should be overridden in child classes.
        '''
        if months.prev is None:
            print 'No previous month.'
        else:
            print 'Previous month: %s-%s' % months.prev
        print 'Current month: %s-%s' % months.cur
        if months.next is None:
            print 'No next month.'
        else:
            print 'Next month: %s-%s' % months.next

        if pages.prev is None:
            print '    No previous page.'
        else:
            print '    Prev', pages.prev
        print '    Index', pages.cur
        if pages.next is None:
            print '    No next page.'
        else:
            print '    Next', pages.next
        for post in posts:
            fmt_str = post.published.strftime('     - %Y-%m-%d-%%s')
            print fmt_str % post.slug


class PostArchiveDaily(PostArchiveBase):
    '''Parse the posts into a list, grouped by day, then by page.

    The :func:``render`` function should be overrridden to actually render the
    posts.

    This depends upon the objs having a value for the key ``posts``.

    '''

    fmt = 'html'

    def key(self, post):
        '''The key for the post.
        '''
        return (post.published.year, post.published.month, post.published.day)

    def rev_key(self, key):
        '''Return a dictionary mapping attributes to values in the key.
        '''
        return {'year': key[0], 'month': key[1], 'day': key[2]}

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
        def action(obj_list, days, pages):
            '''The action to pass to split_paginate_action.
            '''
            ret.append(self.path(page=pages.cur, year=days.cur[0],
                month=days.cur[1], day=days.cur[2]))
        paginate.split_paginate_action(self.settings.POSTS_PER_PAGE,
                self.key, self._sorted_posts(), action)
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> settings.POSTS_PER_PAGE = 1
        >>> pad = PostArchiveDaily(settings, objs, urlmapper)
        >>> pad.write()
        No previous day.
        Current day: 2010-2-2
        Next day: 2010-2-1
            No previous page.
            Index 1
            Next 2
             - 2010-02-02-newday2
        No previous day.
        Current day: 2010-2-2
        Next day: 2010-2-1
            Prev 1
            Index 2
            No next page.
             - 2010-02-02-newday
        Previous day: 2010-2-2
        Current day: 2010-2-1
        Next day: 2010-1-1
            No previous page.
            Index 1
            No next page.
             - 2010-02-01-newmonth
        Previous day: 2010-2-1
        Current day: 2010-1-1
        Next day: 2009-12-31
            No previous page.
            Index 1
            No next page.
             - 2010-01-01-newyear
        Previous day: 2010-1-1
        Current day: 2009-12-31
        No next day.
            No previous page.
            Index 1
            No next page.
             - 2009-12-31-party

        '''
        paginate.split_paginate_action(self.settings.POSTS_PER_PAGE,
                self.key, self._sorted_posts(), self.render)

    def render(self, posts, days, pages):
        '''Render the page corresponding to a single day/page.

        This should be overridden in child classes.
        '''
        if days.prev is None:
            print 'No previous day.'
        else:
            print 'Previous day: %s-%s-%s' % days.prev
        print 'Current day: %s-%s-%s' % days.cur
        if days.next is None:
            print 'No next day.'
        else:
            print 'Next day: %s-%s-%s' % days.next

        if pages.prev is None:
            print '    No previous page.'
        else:
            print '    Prev', pages.prev
        print '    Index', pages.cur
        if pages.next is None:
            print '    No next page.'
        else:
            print '    Next', pages.next
        for post in posts:
            fmt_str = post.published.strftime('     - %Y-%m-%d-%%s')
            print fmt_str % post.slug


class PostSingle(PostWriter):
    '''Parse the posts into single pages.
    '''

    fmt = 'html'

    def path(self, post):
        '''Use the urlmapper to construct a path for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, type='post', year=post.published.year,
                month=post.published.month, day=post.published.day,
                slug=post.slug)

    def url(self, post):
        '''Use the urlmapper to construct a URL for the given attributes.
        '''
        urlfor = self.urlmapper.urlfor
        return urlfor(self.fmt, absolute=True, type='post',
                year=post.published.year, month=post.published.month,
                day=post.published.day, slug=post.slug)

    def urls(self):
        '''A list of rooted paths that are the path component of URLs.

        Example on testdata/pristine::

            >>> c = components
            >>> urlmapper.add(c.Type('post')/c.year/c.month/c.day/c.slug)
            >>> ps = PostSingle(settings, objs, urlmapper)
            >>> pprint(ps.urls())
            ['2010/02/02/newday2/index.html',
             '2010/02/02/newday/index.html',
             '2010/02/01/newmonth/index.html',
             '2010/01/01/newyear/index.html',
             '2009/12/31/party/index.html']

        '''
        ret = list()
        for post in self._sorted_posts():
            ret.append(self.path(post=post))
        return ret

    def write(self):
        '''Write the parsed posts to the filesystem.

        Example on testdata/pristine::

        >>> ps = PostSingle(settings, objs, urlmapper)
        >>> ps.write()
        Post 2010/02/02/newday2
        Post 2010/02/02/newday
        Post 2010/02/01/newmonth
        Post 2010/01/01/newyear
        Post 2009/12/31/party

        '''
        for post in self._sorted_posts():
            self.render(post)

    def render(self, post):
        '''Render the posts.

        This should be overridden in child classes.
        '''
        print 'Post %s/%s' % (post.published.strftime('%Y/%m/%d'), post.slug)


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
    s = {'PARSERS': {'posts': 'firmant.parsers.posts.PostParser'}
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        ,'PERMALINK_ROOT': 'http://test'
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    firmant.parse()
    self.globs['settings'] = settings
    self.globs['objs']  = firmant.objs
    self.globs['urlmapper'] = URLMapper(root=settings.PERMALINK_ROOT)
    self.globs['components'] = components
