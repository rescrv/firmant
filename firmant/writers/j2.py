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


'''Writers that inherit from other writers and render html.
'''


import abc
import os

import jinja2

from firmant import writers
import firmant.writers.staticrst
import firmant.writers.posts
from firmant.utils import paths
from firmant.utils import workarounds


class Jinja2Base(object):
    '''Base class used for functionality common to all J2 writers.
    '''

    def __init__(self, environment, objects, *args, **kwargs):
        super(Jinja2Base, self).__init__(environment, objects, *args, **kwargs)
        settings = environment['settings']
        self.__environment__ = environment
        self.__objects__ = objects
        loader = jinja2.FileSystemLoader(settings.TEMPLATE_DIR)
        self.__j2env__ = jinja2.Environment(loader=loader)

    def render_to_file(self, path, template, context):
        '''Render template with context and save to path.
        '''
        template = self.__j2env__.get_template(template)
        globs    = self.__environment__.get('j2globals', dict())
        globs.update(context)
        data     = template.render(globs)
        out      = paths.create_or_truncate(path)
        out.write(data.encode('utf-8'))
        out.flush()
        out.close()


class Jinja2StaticRst(Jinja2Base, writers.staticrst.StaticRstWriter):
    '''Render staticrst objects using the :class:`StaticRstWriter` base.
    '''

    extension = 'html'

    template = 'flat.html'

    def render(self, environment, path, obj):
        '''Render the data in a Jinja2 template.

        .. doctest::
           :hide:

           >>> import tempfile
           >>> path = tempfile.NamedTemporaryFile(delete=False).name
           >>> objs = {'staticrst': objects.staticrst}

        .. doctest::

           >>> j2sr = Jinja2StaticRst(environment, objs)
           >>> obj = j2sr.obj_list(environment, objs)[0]
           >>> j2sr.render(environment, path, obj)
           >>> cat(path)
           About at about

        .. doctest::
           :hide:

           >>> os.unlink(path)

        '''
        context = dict()
        context['path'] = obj.path
        context['page'] = obj
        self.render_to_file(path, self.template, context)


class Jinja2PostWriter(Jinja2Base, writers.posts.PostWriter):
    '''Render each post individually using Jinja2 templates.
    '''

    extension = 'html'

    template = 'posts/single.html'

    def render(self, environment, path, post):
        r'''Render the data in a Jinja2 template.

        .. doctest::
           :hide:

           >>> import tempfile
           >>> path = tempfile.NamedTemporaryFile(delete=False).name
           >>> objs = {'posts': objects.posts}

        .. doctest::

           >>> j2pw = Jinja2PostWriter(environment, objs)
           >>> obj = j2pw.obj_list(environment, objs)[0]
           >>> j2pw.render(environment, path, obj)
           >>> cat(path)
           2009-12-31 | party by John Doe

        .. doctest::
           :hide:

           >>> os.unlink(path)

        '''
        context = dict()
        context['post']  = post
        self.render_to_file(path, self.template, context)


class Jinja2PostArchiveBase(Jinja2Base):
    '''Common functionality for rendering Jinja2 archive views.
    '''

    __metaclass__ = abc.ABCMeta

    extension = 'html'

    @workarounds.abstractproperty
    def template(self): pass

    def render(self, environment, path, obj):
        key = self.key(obj)
        context = dict()
        context['posts'] = obj[0]
        urlmapper = environment['urlmapper']
        if len(obj) == 3:
            pages = 2
            calen = 1
        elif len(obj) == 2:
            pages = 1
            calen = False
        # Construct the urls for prev/next paginated pages
        if obj[pages].prev:
            d = key.copy()
            d['page'] = obj[pages].prev
            context['page_prev'] = urlmapper.url(self.extension, **d)
        else:
            context['page_prev'] = None
        if obj[pages].next:
            d = key.copy()
            d['page'] = obj[pages].next
            context['page_next'] = urlmapper.url(self.extension, **d)
        else:
            context['page_next'] = None
        # Construct the urls for prev/next archive pages
        if calen and obj[calen].prev:
            d = key.copy()
            d['page'] = 1
            if len(obj[1].prev) >= 1:
                d['year'] = obj[calen].prev[0]
            if len(obj[1].prev) >= 2:
                d['month'] = obj[calen].prev[1]
            if len(obj[1].prev) >= 3:
                d['day'] = obj[calen].prev[2]
            context['cal_prev'] = urlmapper.url(self.extension, **d)
        else:
            context['cal_prev'] = None
        if calen and obj[calen].next:
            d = key.copy()
            d['page'] = 1
            if len(obj[1].next) >= 1:
                d['year'] = obj[calen].next[0]
            if len(obj[1].next) >= 2:
                d['month'] = obj[calen].next[1]
            if len(obj[1].next) >= 3:
                d['day'] = obj[calen].next[2]
            context['cal_next'] = urlmapper.url(self.extension, **d)
        else:
            context['cal_next'] = None
        self.render_to_file(path, self.template, context)


class Jinja2PostArchiveAll(Jinja2PostArchiveBase, writers.posts.PostArchiveAll):
    template = 'posts/archive_all.html'


class Jinja2PostArchiveYearly(Jinja2PostArchiveBase,
        writers.posts.PostArchiveYearly):
    template = 'posts/archive_yearly.html'


class Jinja2PostArchiveMonthly(Jinja2PostArchiveBase,
        writers.posts.PostArchiveMonthly):
    template = 'posts/archive_monthly.html'


class Jinja2PostArchiveDaily(Jinja2PostArchiveBase,
        writers.posts.PostArchiveDaily):
    template = 'posts/archive_daily.html'


def _setup(self):
    '''Setup the test cases.
    '''
    import tempfile
    from minimock import Mock

    from pysettings.settings import Settings
    from firmant.application import Firmant
    from firmant.routing import URLMapper
    from firmant.routing import components
    from firmant.utils.paths import cat
    s = {'PARSERS': {'posts': 'firmant.parsers.posts.PostParser'
                    ,'staticrst': 'firmant.parsers.static.StaticRstParser'}
        ,'CONTENT_ROOT': 'testdata/pristine'
        ,'POSTS_SUBDIR': 'posts'
        ,'STATIC_RST_SUBDIR': 'flat'
        ,'REST_EXTENSION': 'rst'
        ,'POSTS_PER_PAGE': 2
        ,'OUTPUT_DIR': tempfile.mkdtemp()
        ,'TEMPLATE_DIR': 'testdata/pristine/templates'
        ,'PERMALINK_ROOT': 'http://testurl'
        }
    settings               = Settings(s)
    firmant                = Firmant(settings)
    firmant.parse()
    from testdata.chunks import c900
    self.globs['settings']   = settings
    self.globs['objs']       = firmant.objs
    self.globs['urlmapper'] = URLMapper(settings.OUTPUT_DIR,
            settings.PERMALINK_ROOT)
    self.globs['Mock']       = Mock
    self.globs['components'] = components
    self.globs['cat']        = cat
    self.globs['environment'] = {'settings': settings
                                ,'urlmapper': self.globs['urlmapper']
                                }
    settings.POSTS_PER_PAGE = 2
    self.globs['settings'] = settings
    self.globs['objects'] = c900


def _teardown(test):
    '''Cleanup the Jinja2 test cases.
    '''
    import shutil
    shutil.rmtree(test.globs['settings'].OUTPUT_DIR)
