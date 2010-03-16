
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
from firmant.writers import posts
from firmant.writers import Writer


class Jinja2Writer(Writer):

    def __init__(self, *args, **kwargs):
        super(Jinja2Writer, self).__init__(*args, **kwargs)
        loader = FileSystemLoader(self.settings.TEMPLATE_DIR)
        self._env = Environment(loader=loader)

    def render_to_file(self, path, template, context):
        template = self._env.get_template(template)
        data     = template.render(context)
        path     = os.path.join(self.settings.OUTPUT_DIR, path or '')
        f        = utils.paths.create_or_truncate(path)
        f.write(data.encode('utf-8'))
        f.flush()
        f.close()


class Jinja2PostArchiveAll(Jinja2Writer, posts.PostArchiveAll):

    fmt = 'html'

    def render(self, page, num_pages, first, last, posts):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> settings.URLMapper.add(c.Type('post')/c.pageno)
            >>> j2paa = Jinja2PostArchiveAll(settings, firmant.objs)
            >>> j2paa.log = Mock('log')
            >>> j2paa.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'index.html'))
            Called stdout.write('Page 1/3\n')
            Called stdout.write('Posts 1-2\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'page2/index.html'))
            Called stdout.write('Page 2/3\n')
            Called stdout.write('Posts 3-4\n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, 'page3/index.html'))
            Called stdout.write('Page 3/3\n')
            Called stdout.write('Posts 5-5\n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.url(page)
        template = 'posts/archive_all.html'
        context = dict()
        context['page_no']       = page
        context['page_max']      = num_pages
        context['first_post_no'] = first
        context['last_post_no']  = last
        context['posts']         = posts
        self.render_to_file(url, template, context)


class Jinja2PostArchiveYearly(Jinja2Writer, posts.PostArchiveYearly):

    fmt = 'html'

    def render(self, year, page, num_pages, first, last, posts):
        r'''Render the data in a Jinja2 template.

            >>> c = components
            >>> settings.URLMapper.add(c.Type('post')/c.year/c.pageno)
            >>> j2pay = Jinja2PostArchiveYearly(settings, firmant.objs)
            >>> j2pay.log = Mock('log')
            >>> j2pay.write()
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/index.html'))
            Called stdout.write('Page 1/2\n')
            Called stdout.write('Posts 1-2\n')
            Called stdout.write('Year 2010\n')
            Called stdout.write('2010-02-02-newday2\n')
            Called stdout.write('2010-02-02-newday\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2010/page2/index.html'))
            Called stdout.write('Page 2/2\n')
            Called stdout.write('Posts 3-4\n')
            Called stdout.write('Year 2010\n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-01-01-newyear\n')
            >>> cat(os.path.join(settings.OUTPUT_DIR, '2009/index.html'))
            Called stdout.write('Page 1/1\n')
            Called stdout.write('Posts 1-1\n')
            Called stdout.write('Year 2009\n')
            Called stdout.write('2009-12-31-party\n')

        '''
        url = self.url(year, page)
        template = 'posts/archive_yearly.html'
        context = dict()
        context['year']          = year
        context['page_no']       = page
        context['page_max']      = num_pages
        context['first_post_no'] = first
        context['last_post_no']  = last
        context['posts']         = posts
        self.render_to_file(url, template, context)


def _setUp(self):
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
    URLMapper(settings)
    firmant                = Firmant(settings)
    firmant.parse()
    self.globs['settings']   = settings
    self.globs['firmant']    = firmant
    self.globs['URLMapper']  = URLMapper
    self.globs['Mock']       = Mock
    self.globs['components'] = components
    self.globs['cat']        = lambda out: cat(out, Mock('stdout'))


def _tearDown(test):
    '''Cleanup the Jinja2 test cases.
    '''
    import shutil
    shutil.rmtree(test.globs['settings'].OUTPUT_DIR)
