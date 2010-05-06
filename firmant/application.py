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


'''The Firmant application.

Orchestrates the high process of parsing, transforming, and writing content.
'''


import logging
import datetime

from pysettings.modules import get_module

from firmant.chunks import AbstractChunk
from firmant.routing import URLMapper
from firmant.utils import class_name


class Firmant(object):
    '''Perform a complete run from parsing through writing.

        >>> from pysettings.loaders import mod_to_settings
        >>> s = mod_to_settings('firmant.settings')
        >>> s.OUTPUT_DIR = outdir
        >>> f = Firmant(s)
        >>> f.log = Mock('log')
        >>> pprint(f.parsers) #doctest: +ELLIPSIS
        {'feeds': <firmant.parsers.feeds.FeedParser object at 0x...>,
         'posts': <firmant.parsers.posts.PostParser object at 0x...>,
         'static': <firmant.parsers.static.StaticParser object at 0x...>,
         'staticrst': <firmant.parsers.static.StaticRstParser object at 0x...>,
         'tags': <firmant.parsers.tags.TagParser object at 0x...>}
        >>> f.parse()
        >>> pprint(f.objs) #doctest: +ELLIPSIS
        {'feeds': [<firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>],
         'posts': [<firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>],
         'static': [static_obj<testdata/pristine/static/images/88x31.png>],
         'staticrst': [<firmant.parsers.RstObject object at 0x...>,
                       <firmant.parsers.RstObject object at 0x...>,
                       <firmant.parsers.RstObject object at 0x...>],
         'tags': [<firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>]}
        >>> f.cross_reference() #doctest: +ELLIPSIS
        >>> f.create_permalinks() #doctest: +ELLIPSIS
        >>> for post in f.objs['posts']:
        ...     pprint((post.tags, post.feeds)) #doctest: +ELLIPSIS
        ([<firmant.parsers.RstObject object at 0x...>],
         [<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>])
        ([<firmant.parsers.RstObject object at 0x...>],
         [<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>])
        ([<firmant.parsers.RstObject object at 0x...>],
         [<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>])
        ([<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>],
         [<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>])
        ([<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>],
         [<firmant.parsers.RstObject object at 0x...>,
          <firmant.parsers.RstObject object at 0x...>])
        >>> f.setup_writers()
        >>> f()

    '''

    def __init__(self, settings):
        self.settings = settings
        self.urlmapper = URLMapper(settings.OUTPUT_DIR, settings.PERMALINK_ROOT,
                getattr(settings, 'URLS', None))
        self.log = logging.getLogger(class_name(self.__class__))

        self.objs = dict()
        self.writers = dict()
        self.chunks = list()
        self.env    = dict()
        self.env['log'] = self.log
        self.env['urlmapper'] = self.urlmapper
        self.env['settings'] = self.settings

        self.chunks.append(CheckURLConflicts())
        self.chunks.append(SetupURLConflicts())

        # Setup parsers
        self.parsers = dict()
        for key, parser in settings.PARSERS.items():
            mod, attr = parser.rsplit('.', 1)
            mod = get_module(mod)
            parser = getattr(mod, attr)
            self.parsers[key] = parser(self.settings)

    def __call__(self):
        while len(self.chunks):
            self.chunks.sort(key = lambda x: x.scheduling_order)
            chunk = self.chunks[0]
            self.env, self.objs, newchunks = chunk(self.env, self.objs)
            self.chunks = self.chunks[1:]
            for c in newchunks:
                if c.scheduling_order <= chunk.scheduling_order:
                    error = _('New chunk violates scheduling_order constraint')
                    self.log.error(error)
                else:
                    self.chunks.append(c)

    def parse(self):
        '''Call parse on each configured parser.
        '''
        # Parse documents
        for key, parser in self.parsers.items():
            self.objs[key] = parser.parse()

    def cross_reference(self):
        '''Cross reference tags and feeds
        '''
        for feed in self.objs.get('feeds', []):
            feed.posts = list()
        for tag in self.objs.get('tags', []):
            tag.posts = list()
        # TODO inefficient, notproud
        for post in self.objs.get('posts', []):
            to_delete = list()
            for i, ptag in enumerate(post.tags):
                seen = False
                for tag in self.objs.get('tags', []):
                    if tag.slug == ptag:
                        seen = True
                        tag.posts.append(post)
                        post.tags[i] = tag
                if not seen:
                    warning  = _("Tag '%s' referenced but not defined.")
                    warning %= ptag
                    self.log.warning(warning)
                    to_delete.append(i)
            for i in reversed(to_delete):
                del post.tags[i]
            to_delete = list()
            for i, pfeed in enumerate(post.feeds):
                seen = False
                for feed in self.objs.get('feeds', []):
                    if feed.slug == pfeed:
                        seen = True
                        feed.posts.append(post)
                        post.feeds[i] = feed
                if not seen:
                    error  = _("Feed '%s' referenced but not defined.")
                    error %= pfeed
                    self.log.error(error)
                    to_delete.append(i)
            for i in reversed(to_delete):
                del post.feeds[i]

    def setup_writers(self):
        '''Create instances of writer classes.
        '''
        for writer in self.settings.WRITERS:
            mod, attr = writer.rsplit('.', 1)
            mod = get_module(mod)
            writer = getattr(mod, attr)
            self.chunks.append(writer(self.env, self.objs))

    def create_permalinks(self):
        '''Add permalinks to objects.
        '''
        # TODO:  Remove prior to 0.2.0
        url = self.urlmapper.url
        for post in self.objs.get('posts', []):
            post.permalink = url('atom', **{'type': 'post'
                                           ,'year': post.published.year
                                           ,'month': post.published.month
                                           ,'day': post.published.day
                                           ,'slug': post.slug
                                           })
        for tag in self.objs.get('tags', []):
            tag.permalink = url('html', **{'type': 'tag'
                                          ,'slug': tag.slug
                                          })
        for feed in self.objs.get('feeds', []):
            feed.permalink = url('atom', **{'type': 'feed'
                                           ,'slug': feed.slug
                                           })

    def create_globals(self):
        '''Create a dictionary of globals to be added to rendering contexts.
        '''
        self.env['j2globals'] = globals = dict()
        url = self.urlmapper.url
        globals['urlfor'] = url
        globals['recent_posts'] = [(p.title, p.permalink) for p in
                reversed(sorted(self.objs.get('posts', []),
                    key=lambda p: (p.published, p.slug)))] \
                [:self.settings.SIDEBAR_POSTS_LEN]
        # TODO:  Disgusted with this.  I will make a real global object later.
        globals['daily_archives'] = \
                [(datetime.date(y, m, d), url('html',
                    type='post', year=y, month=m, day=d, page=1))
                for y, m, d in reversed(sorted(set([(p.published.year,
                    p.published.month, p.published.day)
                    for p in self.objs.get('posts', [])])))] \
                [:self.settings.SIDEBAR_ARCHIVES_LEN]
        globals['monthly_archives'] = \
                [(datetime.date(y, m, 1), url('html',
                    type='post', year=y, month=m, page=1))
                for y, m in reversed(sorted(set([(p.published.year, p.published.month)
                    for p in self.objs.get('posts', [])])))] \
                [:self.settings.SIDEBAR_ARCHIVES_LEN]
        globals['yearly_archives'] = \
                [(datetime.date(y, 1, 1), url('html',
                    type='post', year=y, page=1))
                for y in reversed(sorted(set([p.published.year
                    for p in self.objs.get('posts', [])])))] \
                [:self.settings.SIDEBAR_ARCHIVES_LEN]
        globals['static_pages'] = [(p.title, p.permalink) for p in
                sorted(self.objs.get('staticrst', []), key=lambda p: p.title)]
        globals['atom_feeds'] = [(f.slug, f.permalink) for f in
                sorted(self.objs.get('feeds', []) , key=lambda f: f.slug)]


class SetupURLConflicts(AbstractChunk):
    '''A chunk that sets up the empty dictionary for URL conflicts.
    '''

    def __call__(self, environment, objects):
        '''Ensure that the sets of URLs are disjoint.
        '''
        environment = environment.copy()
        environment['urls'] = dict()
        return environment, objects, []

    scheduling_order = 499


class CheckURLConflicts(AbstractChunk):
    '''A chunk that warns of writers with conflicting URLs.
    '''

    def __call__(self, environment, objects):
        '''Ensure that the sets of URLs are disjoint.
        '''
        urls = dict()
        for key, inst in environment['urls'].items():
            for url in inst:
                if url is None:
                    warning  = _("Writer %s's URLs incompletely defined.")
                    warning %= key
                    environment['log'].warning(warning)
                elif url in urls:
                    warning  = _('Writers %s and %s conflict over %s.')
                    warning %= urls[url], key, url
                    environment['log'].warning(warning)
                else:
                    urls[url] = key
        return (environment, objects, [])

    scheduling_order = 600


def _setup(self):
    '''Setup the test cases.

    Actions taken::

        - Create a temporary directory.

    '''
    import tempfile
    self.globs['outdir'] = tempfile.mkdtemp()


def _teardown(test):
    '''Cleanup the test cases.

    Actions taken::

        - Remove the temporary directory.

    '''
    import shutil
    shutil.rmtree(test.globs['outdir'])
