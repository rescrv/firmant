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


import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

from firmant import utils
from firmant.utils import paths
from firmant.writers import posts
from firmant.writers import Writer


class Jinja2Writer(Writer):

    def __init__(self, *args, **kwargs):
        super(Jinja2Writer, self).__init__(*args, **kwargs)
        loader = FileSystemLoader(self.settings.TEMPLATE_DIR)
        self._env = Environment(loader=loader)

    def render_to_file(self, path, template, context):
        '''Render template with context and save to path.
        '''
        template = self._env.get_template(template)
        data     = template.render(context)
        path     = os.path.join(self.settings.OUTPUT_DIR, path or '')
        f        = paths.create_or_truncate(path)
        f.write(data.encode('utf-8'))
        f.flush()
        f.close()


class Jinja2PostArchiveAll(Jinja2Writer, posts.PostArchiveAll):
    '''Render paginated post lists with Jinja2 templates.
    '''

    fmt = 'html'

    def render(self, post_list, pages):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> urlmapper.add(c.Type('post')/c.pageno)
            >>> j2paa = Jinja2PostArchiveAll(settings, objs, urlmapper)
            >>> j2paa.log = Mock('log')
            >>> j2paa.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'index.html'))
            Called stdout.write('Prev: \n')
            Called stdout.write('Next: page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'page2/index.html'))
            Called stdout.write('Prev: index.html\n')
            Called stdout.write('Next: page3/index.html\n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'page3/index.html'))
            Called stdout.write('Prev: page2/index.html\n')
            Called stdout.write('Next: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.url(page=pages.cur)
        template = 'posts/archive_all.html'
        context = dict()
        if pages.prev is not None:
            prev = self.url(page=pages.prev)
        else:
            prev = None
        if pages.next is not None:
            nex = self.url(page=pages.next)
        else:
            nex = None
        context['prev']          = prev
        context['next']          = nex
        context['posts']         = post_list
        self.render_to_file(url, template, context)


class Jinja2PostArchiveYearly(Jinja2Writer, posts.PostArchiveYearly):
    '''Render paginated post lists (grouped by year) with Jinja2 templates.
    '''

    fmt = 'html'

    def render(self, post_list, years, pages):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> urlmapper.add(c.Type('post')/c.year/c.pageno)
            >>> j2pay = Jinja2PostArchiveYearly(settings, objs, urlmapper)
            >>> j2pay.log = Mock('log')
            >>> j2pay.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/index.html'))
            Called stdout.write('Prev year: \n')
            Called stdout.write('Next year: 2009/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: 2010/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/page2/index.html'))
            Called stdout.write('Prev year: \n')
            Called stdout.write('Next year: 2009/index.html\n')
            Called stdout.write('Prev page: 2010/index.html\n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/index.html'))
            Called stdout.write('Prev year: 2010/index.html\n')
            Called stdout.write('Next year: \n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.url(page=pages.cur, year=years.cur[0])
        template = 'posts/archive_yearly.html'
        context = dict()
        if years.prev is not None:
            sprev = self.url(page=1, year=years.prev[0])
        else:
            sprev = None
        if years.next is not None:
            snext = self.url(page=1, year=years.next[0])
        else:
            snext = None
        if pages.prev is not None:
            pprev = self.url(page=pages.prev, year=years.cur[0])
        else:
            pprev = None
        if pages.next is not None:
            pnext = self.url(page=pages.next, year=years.cur[0])
        else:
            pnext = None
        context['year']           = years.cur[0]
        context['pprev']          = pprev
        context['pnext']          = pnext
        context['sprev']          = sprev
        context['snext']          = snext
        context['posts']         = post_list
        self.render_to_file(url, template, context)


class Jinja2PostArchiveMonthly(Jinja2Writer, posts.PostArchiveMonthly):

    fmt = 'html'

    def render(self, post_list, months, pages):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> urlmapper.add(
            ...     c.Type('post')/c.year/c.month/c.pageno)
            >>> j2pam = Jinja2PostArchiveMonthly(settings, objs, urlmapper)
            >>> j2pam.log = Mock('log')
            >>> j2pam.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/index.html'))
            Called stdout.write('Prev month: \n')
            Called stdout.write('Next month: 2010/01/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: 2010/02/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/page2/index.html'))
            Called stdout.write('Prev month: \n')
            Called stdout.write('Next month: 2010/01/index.html\n')
            Called stdout.write('Prev page: 2010/02/index.html\n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-01-newmonth\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/01/index.html'))
            Called stdout.write('Prev month: 2010/02/index.html\n')
            Called stdout.write('Next month: 2009/12/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/12/index.html'))
            Called stdout.write('Prev month: 2010/01/index.html\n')
            Called stdout.write('Next month: \n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.url(page=pages.cur, year=months.cur[0], month=months.cur[1])
        template = 'posts/archive_monthly.html'
        context = dict()
        if months.prev is not None:
            sprev = self.url(page=1, year=months.prev[0], month=months.prev[1])
        else:
            sprev = None
        if months.next is not None:
            snext = self.url(page=1, year=months.next[0], month=months.next[1])
        else:
            snext = None
        if pages.prev is not None:
            pprev = self.url(page=pages.prev, year=months.cur[0],
                    month=months.cur[1])
        else:
            pprev = None
        if pages.next is not None:
            pnext = self.url(page=pages.next, year=months.cur[0],
                    month=months.cur[1])
        else:
            pnext = None
        context['year']           = months.cur[0]
        context['month']          = months.cur[1]
        context['pprev']          = pprev
        context['pnext']          = pnext
        context['sprev']          = sprev
        context['snext']          = snext
        context['posts']          = post_list
        self.render_to_file(url, template, context)


class Jinja2PostArchiveDaily(Jinja2Writer, posts.PostArchiveDaily):

    fmt = 'html'

    def render(self, post_list, days, pages):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> settings.POSTS_PER_PAGE = 1
            >>> urlmapper.add(
            ...     c.Type('post')/c.year/c.month/c.day/c.pageno)
            >>> j2pad = Jinja2PostArchiveDaily(settings, objs, urlmapper)
            >>> j2pad.log = Mock('log')
            >>> j2pad.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/02/index.html'))
            Called stdout.write('Prev day: \n')
            Called stdout.write('Next day: 2010/02/01/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: 2010/02/02/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/02/page2/index.html'))
            Called stdout.write('Prev day: \n')
            Called stdout.write('Next day: 2010/02/01/index.html\n')
            Called stdout.write('Prev page: 2010/02/02/index.html\n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/01/index.html'))
            Called stdout.write('Prev day: 2010/02/02/index.html\n')
            Called stdout.write('Next day: 2010/01/01/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-01-newmonth\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/01/01/index.html'))
            Called stdout.write('Prev day: 2010/02/01/index.html\n')
            Called stdout.write('Next day: 2009/12/31/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/12/31/index.html'))
            Called stdout.write('Prev day: 2010/01/01/index.html\n')
            Called stdout.write('Next day: \n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.url(page=pages.cur, year=days.cur[0], month=days.cur[1],
                day=days.cur[2])
        template = 'posts/archive_daily.html'
        context = dict()
        if days.prev is not None:
            sprev = self.url(page=1, year=days.prev[0], month=days.prev[1],
                    day=days.prev[2])
        else:
            sprev = None
        if days.next is not None:
            snext = self.url(page=1, year=days.next[0], month=days.next[1],
                    day=days.next[2])
        else:
            snext = None
        if pages.prev is not None:
            pprev = self.url(page=pages.prev, year=days.cur[0],
                    month=days.cur[1], day=days.cur[2])
        else:
            pprev = None
        if pages.next is not None:
            pnext = self.url(page=pages.next, year=days.cur[0],
                    month=days.cur[1], day=days.cur[2])
        else:
            pnext = None
        context['year']           = days.cur[0]
        context['month']          = days.cur[1]
        context['day']            = days.cur[2]
        context['pprev']          = pprev
        context['pnext']          = pnext
        context['sprev']          = sprev
        context['snext']          = snext
        context['posts']          = post_list
        self.render_to_file(url, template, context)


class Jinja2PostSingle(Jinja2Writer, posts.PostSingle):

    fmt = 'html'

    def render(self, post):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> urlmapper.add(c.Type('post')/c.year/c.month/c.day/c.slug)
            >>> j2ps = Jinja2PostSingle(settings, objs, urlmapper)
            >>> j2ps.log = Mock('log')
            >>> j2ps.write()
            >>> join = os.path.join
            >>> cat(join(settings.OUTPUT_DIR, '2010/02/02/newday2/index.html'))
            Called stdout.write('2010-02-02 | newday2 by John Doe')
            >>> cat(join(settings.OUTPUT_DIR, '2010/02/02/newday/index.html'))
            Called stdout.write('2010-02-02 | newday by John Doe')
            >>> cat(join(settings.OUTPUT_DIR, '2010/02/01/newmonth/index.html'))
            Called stdout.write('2010-02-01 | newmonth by John Doe')
            >>> cat(join(settings.OUTPUT_DIR, '2010/01/01/newyear/index.html'))
            Called stdout.write('2010-01-01 | newyear by John Doe')
            >>> cat(join(settings.OUTPUT_DIR, '2009/12/31/party/index.html'))
            Called stdout.write('2009-12-31 | party by John Doe')

        '''
        url = self.url(year=post.published.year, month=post.published.month,
                day=post.published.day, slug=post.slug)
        template = 'posts/single.html'
        context = dict()
        context['year']          = post.published.year
        context['month']         = post.published.month
        context['day']           = post.published.day
        context['slug']          = post.slug
        context['post']          = post
        self.render_to_file(url, template, context)


def _setup(self):
    import tempfile
    from minimock import Mock

    from pysettings.settings import Settings
    from firmant.application import Firmant
    from firmant.routing import URLMapper
    from firmant.routing import components
    from firmant.utils.paths import cat
    s = {'PARSERS': {'posts': 'firmant.parsers.posts.PostParser'}
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        ,'OUTPUT_DIR': tempfile.mkdtemp()
        ,'TEMPLATE_DIR': 'testdata/pristine/templates'
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    firmant.parse()
    self.globs['settings']   = settings
    self.globs['objs']       = firmant.objs
    self.globs['urlmapper']  = URLMapper()
    self.globs['Mock']       = Mock
    self.globs['components'] = components
    self.globs['cat']        = lambda out: cat(out, Mock('stdout'))


def _teardown(test):
    '''Cleanup the Jinja2 test cases.
    '''
    import shutil
    shutil.rmtree(test.globs['settings'].OUTPUT_DIR)
