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


'''Setup Jinja2 globals (objects that should be available in Jinja2 templates).

Each Jinja2 writer will make the globals available in the context when rendering
templates.
'''


import datetime

from firmant import chunks
from firmant import decorators
from firmant.utils import workarounds
from firmant.writers import j2


class Global(chunks.AbstractChunk):
    '''Base class for other globals providers.

    Globals inject themselves into the environment[Jinja2Base]['globals']
    dictionary.

    :meth`__call__` will call :meth:`add_glob` with a dictionary, the
    environment and the objects.  The dictionary should be modified directly.
    '''

    def __init__(self, environment, objects):
        # pylint: disable-msg=W0613
        super(Global, self).__init__()

    def __call__(self, environment, objects):
        globs = self._get_globals_dict(environment)
        self.add_glob(globs, environment, objects)
        return environment, objects, []

    @workarounds.abstractmethod
    def add_glob(self, globs, environment, objects):
        '''Add the necessary globals to the dictionary `globs`.

        This dictionary will be copied for use in each Jinja2 context.
        '''

    @staticmethod
    def _get_globals_dict(environment):
        '''Return a the globals dictionary, creating it and the Jinja2
        environment if necessary.
        '''
        j2env = environment.get(j2.Jinja2Base, None)
        if j2env is None:
            environment[j2.Jinja2Base] = j2env = {}
        globs = j2env.get('globals', None)
        if globs is None:
            j2env['globals'] = globs = {}
        return globs

    scheduling_order = 800


class URLFor(Global):
    '''Add the function :func:`urlfor` to globals.

    The :func:`urlfor` is the :meth:`url` method of a
    :class:`firmant.routingURLMapper` object.
    '''

    @decorators.in_environment('urlmapper')
    def add_glob(self, globs, environment, objects):
        '''Create the ``urlfor`` global.
        '''
        globs['urlfor'] = environment['urlmapper'].url


def _sorted_posts(objects, newest_first=True):
    '''Return a list of sorted posts from objects
    '''
    return sorted(objects.get('post', []), reverse=newest_first,
                  key=lambda p: (p.published, p.slug))


class RecentPosts(Global):
    '''Add a list of the `SIDEBAR_POSTS_LEN` most recent posts to globals.
    '''

    @decorators.in_environment('settings')
    def add_glob(self, globs, environment, objects):
        '''Put the list of posts under the key ``recent_posts``.
        '''
        offset = environment['settings'].SIDEBAR_POSTS_LEN
        posts = _sorted_posts(objects)[:offset]
        globs['recent_posts'] = [(p.title, p.permalink) for p in posts]


class DailyArchives(Global):
    '''Add a list of the `SIDEBAR_POSTS_LEN` most recent daily archives to
    globals.
    '''

    @decorators.in_environment('settings')
    @decorators.in_environment('urlmapper')
    def add_glob(self, globs, environment, objects):
        '''Put the list of daily archives under the key ``daily_archives``.
        '''
        url = environment['urlmapper'].url
        offset = environment['settings'].SIDEBAR_POSTS_LEN
        posts = _sorted_posts(objects)
        archives = set([(p.published.year, p.published.month, p.published.day)
                        for p in posts])
        globs['daily_archives'] = [(datetime.date(y, m, d),
                                     url('html', type='post', year=y, month=m,
                                         day=d, page=1))
                                     for y, m, d in
                                     sorted(archives, reverse=True)][:offset]


class MonthlyArchives(Global):
    '''Add a list of the `SIDEBAR_POSTS_LEN` most recent monthly archives to
    globals.
    '''

    @decorators.in_environment('settings')
    @decorators.in_environment('urlmapper')
    def add_glob(self, globs, environment, objects):
        '''Put the list of monthly archives under the key ``monthly_archives``.
        '''
        url = environment['urlmapper'].url
        offset = environment['settings'].SIDEBAR_POSTS_LEN
        posts = _sorted_posts(objects)
        archives = set([(p.published.year, p.published.month) for p in posts])
        globs['monthly_archives'] = [(datetime.date(y, m, 1),
                                     url('html', type='post', year=y, month=m,
                                         page=1))
                                     for y, m in
                                     sorted(archives, reverse=True)][:offset]


class YearlyArchives(Global):
    '''Add a list of the `SIDEBAR_POSTS_LEN` most recent yearly archives to
    globals.
    '''

    @decorators.in_environment('settings')
    @decorators.in_environment('urlmapper')
    def add_glob(self, globs, environment, objects):
        '''Put the list of yearly archives under the key ``yearly_archives``.
        '''
        url = environment['urlmapper'].url
        offset = environment['settings'].SIDEBAR_POSTS_LEN
        posts = _sorted_posts(objects)
        archives = set([(p.published.year) for p in posts])
        globs['yearly_archives'] = [(datetime.date(y, 1, 1),
                                     url('html', type='post', year=y, page=1))
                                     for y in
                                     sorted(archives, reverse=True)][:offset]


class StaticPages(Global):
    '''Add a list of the static pages, sorted by title.
    '''

    def add_glob(self, globs, environment, objects):
        '''Put a list of all static pages under the key ``static_pages``.
        '''
        globs['static_pages'] = [(p.title, p.permalink) for p in
                sorted(objects.get('staticrst', []), key=lambda p: p.title)]


class AtomFeeds(Global):
    '''Add a list of the atom feeds, sorted by slug.
    '''

    def add_glob(self, globs, environment, objects):
        '''Put a list of all static pages under the key ``atom_feeds``.
        '''
        globs['atom_feeds'] = [(f.slug, f.permalink) for f in
                sorted(objects.get('feed', []) , key=lambda f: f.slug)]
