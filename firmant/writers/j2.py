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


'''Writers that use the Jinja2 templating engine to create html.
'''


import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

from firmant import utils
from firmant.utils import paths
from firmant.writers import posts
from firmant.writers import Writer


class Jinja2Writer(Writer):
    '''Base class used for functionality common to all J2 writers.
    '''

    def __init__(self, *args, **kwargs):
        super(Jinja2Writer, self).__init__(*args, **kwargs)
        loader = FileSystemLoader(self.settings.TEMPLATE_DIR)
        self._env = Environment(loader=loader)

    def render_to_file(self, path, template, context):
        '''Render template with context and save to path.
        '''
        template = self._env.get_template(template)
        globals  = self.objs.get('globals', dict())
        globals.update(context)
        data     = template.render(globals)
        path     = os.path.join(self.settings.OUTPUT_DIR, path or '')
        f        = paths.create_or_truncate(path)
        f.write(data.encode('utf-8'))
        f.flush()
        f.close()


class Jinja2PostArchiveBase(Jinja2Writer, posts.PostArchiveBase):
    '''Common functionality for rendering Jinja2 archive views.
    '''

    def render_common(self, post_list, cal, pages):
        '''Return the url, template, and context, ready to render.
        '''
        rev      = self.rev_key(cal.cur)
        url      = self.path(page=pages.cur, **rev)
        template = self.template
        context  = dict()
        context.update(rev)
        context['posts'] = post_list
        context['pprev'] = pages.prev and \
                self.path(absolute=True, page=pages.prev, **rev)
        context['pnext'] = pages.next and \
                self.path(absolute=True, page=pages.next, **rev)
        context['sprev'] = cal.prev and \
                self.path(absolute=True, page=1, **self.rev_key(cal.prev))
        context['snext'] = cal.next and \
                self.path(absolute=True, page=1, **self.rev_key(cal.next))
        return url, template, context


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
            Called stdout.write('Next: http://test/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'page2/index.html'))
            Called stdout.write('Prev: http://test/index.html\n')
            Called stdout.write('Next: http://test/page3/index.html\n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'page3/index.html'))
            Called stdout.write('Prev: http://test/page2/index.html\n')
            Called stdout.write('Next: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.path(page=pages.cur)
        template = 'posts/archive_all.html'
        context = dict()
        if pages.prev is not None:
            prev = self.path(absolute=True, page=pages.prev)
        else:
            prev = None
        if pages.next is not None:
            nex = self.path(absolute=True, page=pages.next)
        else:
            nex = None
        context['prev']          = prev
        context['next']          = nex
        context['posts']         = post_list
        self.render_to_file(url, template, context)


class Jinja2PostArchiveYearly(Jinja2PostArchiveBase, posts.PostArchiveYearly):
    '''Render paginated post lists (grouped by year) with Jinja2 templates.
    '''

    fmt = 'html'

    template = 'posts/archive_yearly.html'

    def render(self, post_list, years, pages):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> urlmapper.add(c.Type('post')/c.year/c.pageno)
            >>> j2pay = Jinja2PostArchiveYearly(settings, objs, urlmapper)
            >>> j2pay.log = Mock('log')
            >>> j2pay.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/index.html'))
            Called stdout.write('Prev year: \n')
            Called stdout.write('Next year: http://test/2009/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: http://test/2010/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/page2/index.html'))
            Called stdout.write('Prev year: \n')
            Called stdout.write('Next year: http://test/2009/index.html\n')
            Called stdout.write('Prev page: http://test/2010/index.html\n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/index.html'))
            Called stdout.write('Prev year: http://test/2010/index.html\n')
            Called stdout.write('Next year: \n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url, template, context = self.render_common(post_list, years, pages)
        self.render_to_file(url, template, context)


class Jinja2PostArchiveMonthly(Jinja2PostArchiveBase, posts.PostArchiveMonthly):
    '''Render paginated post lists (grouped by month) with Jinja2 templates.
    '''

    fmt = 'html'

    template = 'posts/archive_monthly.html'

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
            Called stdout.write('Next month: http://test/2010/01/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: http://test/2010/02/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/page2/index.html'))
            Called stdout.write('Prev month: \n')
            Called stdout.write('Next month: http://test/2010/01/index.html\n')
            Called stdout.write('Prev page: http://test/2010/02/index.html\n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-01-newmonth\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/01/index.html'))
            Called stdout.write('Prev month: http://test/2010/02/index.html\n')
            Called stdout.write('Next month: http://test/2009/12/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/12/index.html'))
            Called stdout.write('Prev month: http://test/2010/01/index.html\n')
            Called stdout.write('Next month: \n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url, template, context = self.render_common(post_list, months, pages)
        self.render_to_file(url, template, context)


class Jinja2PostArchiveDaily(Jinja2PostArchiveBase, posts.PostArchiveDaily):
    '''Render paginated post lists (grouped by day) with Jinja2 templates.
    '''

    fmt = 'html'

    template = 'posts/archive_daily.html'

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
            Called stdout.write('Next day: http://test/2010/02/01/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: http://test/2010/02/02/page2/index.html\n')
            Called stdout.write('2010-02-02-newday2\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/02/page2/index.html'))
            Called stdout.write('Prev day: \n')
            Called stdout.write('Next day: http://test/2010/02/01/index.html\n')
            Called stdout.write('Prev page: http://test/2010/02/02/index.html\n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/02/01/index.html'))
            Called stdout.write('Prev day: http://test/2010/02/02/index.html\n')
            Called stdout.write('Next day: http://test/2010/01/01/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-02-01-newmonth\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/01/01/index.html'))
            Called stdout.write('Prev day: http://test/2010/02/01/index.html\n')
            Called stdout.write('Next day: http://test/2009/12/31/index.html\n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/12/31/index.html'))
            Called stdout.write('Prev day: http://test/2010/01/01/index.html\n')
            Called stdout.write('Next day: \n')
            Called stdout.write('Prev page: \n')
            Called stdout.write('Next page: \n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url, template, context = self.render_common(post_list, days, pages)
        self.render_to_file(url, template, context)


class Jinja2PostSingle(Jinja2Writer, posts.PostSingle):
    '''Render each post using Jinja2 templates.
    '''

    fmt = 'html'

    permalinks_for = 'posts'

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
        url = self.path(post=post)
        template = 'posts/single.html'
        context = dict()
        context['year']          = post.published.year
        context['month']         = post.published.month
        context['day']           = post.published.day
        context['slug']          = post.slug
        context['post']          = post
        self.render_to_file(url, template, context)


def _setup(self):
    '''Setup the test cases.

    Actions taken::

        - Create a temporary directory.
        - Create a ``Settings`` object.
        - Create a ``Firmant`` object.
        - Load modules used in tests.

    '''
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
        ,'PERMALINK_ROOT': 'http://test'
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    firmant.parse()
    self.globs['settings']   = settings
    self.globs['objs']       = firmant.objs
    self.globs['urlmapper']  = URLMapper(root=settings.PERMALINK_ROOT)
    self.globs['Mock']       = Mock
    self.globs['components'] = components
    self.globs['cat']        = lambda out: cat(out, Mock('stdout'))


def _teardown(test):
    '''Cleanup the Jinja2 test cases.
    '''
    import shutil
    shutil.rmtree(test.globs['settings'].OUTPUT_DIR)
