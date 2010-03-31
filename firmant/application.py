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

from pysettings.modules import get_module

from firmant.i18n import _
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
         'tags': [<firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>]}
        >>> f.cross_reference() #doctest: +ELLIPSIS
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
        >>> f.check_url_conflicts()
        >>> f.create_permalinks()
        Called log.warning('Object type feeds has no permalink providers.')
        Called log.warning('Object type tags has no permalink providers.')
        >>> pprint([post.permalink for post in f.objs['posts']])
        ['2009/12/31/party/index.html',
         '2010/01/01/newyear/index.html',
         '2010/02/01/newmonth/index.html',
         '2010/02/02/newday/index.html',
         '2010/02/02/newday2/index.html']
        >>> f.write()

    '''

    def __init__(self, settings):
        self.settings = settings
        self.urlmapper = URLMapper(getattr(settings, 'URLS', None))
        self.log = logging.getLogger(class_name(self.__class__))

        self.objs = dict()
        self.writers = dict()

        # Setup parsers
        self.parsers = dict()
        for key, parser in settings.PARSERS.items():
            mod, attr = parser.rsplit('.', 1)
            mod = get_module(mod)
            parser = getattr(mod, attr)
            self.parsers[key] = parser(self.settings)

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
            for i, ptag in enumerate(post.tags):
                for tag in self.objs.get('tags', []):
                    if tag.slug == ptag:
                        tag.posts.append(post)
                        post.tags[i] = tag
            for i, pfeed in enumerate(post.feeds):
                for feed in self.objs.get('feeds', []):
                    if feed.slug == pfeed:
                        feed.posts.append(post)
                        post.feeds[i] = feed

    def setup_writers(self):
        '''Create instances of writer classes.
        '''
        writers = self.writers
        for writer in self.settings.WRITERS:
            mod, attr = writer.rsplit('.', 1)
            mod = get_module(mod)
            writer = getattr(mod, attr)
            # We do not retain the class name from settings as it may be the
            # case that:
            # from foo import Quux
            # really imports the class foo.bar.baz.Quux as Quux was imported
            # into the foo namespace.
            writers[class_name(writer)] = writer(self.settings, self.objs,
                    self.urlmapper)

    def check_url_conflicts(self):
        '''Create instances of writer classes.
        '''
        urls = dict()
        for key, inst in self.writers.items():
            for url in inst.urls():
                if url is None:
                    warning  = _("Writer %s's URLs incompletely defined.")
                    warning %= key
                    self.log.warning(warning)
                elif url in urls:
                    warning  = _('Writers %s and %s conflict over %s.')
                    warning %= urls[url], key, url
                    self.log.warning(warning)
                else:
                    urls[url] = key

    def create_permalinks(self):
        '''Add a 'permalink' attribute to each parsed object.
        '''
        permalink_providers = dict()
        for inst in self.writers.values():
            if hasattr(inst, 'permalinks_for'):
                p_for = inst.permalinks_for
                if p_for in permalink_providers:
                    warning  = _("Object type '%s' has multiple "
                                 "permalink providers.")
                    warning %= p_for
                    self.log.warning(warning)
                else:
                    permalink_providers[p_for] = inst.url
        for obj_tag, obj_list in self.objs.items():
            if obj_tag in permalink_providers:
                url_for = permalink_providers[obj_tag]
                for obj in obj_list:
                    setattr(obj, 'permalink', url_for(obj))
            else:
                warning  = _("Object type %s has no permalink providers.")
                warning %= obj_tag
                self.log.warning(warning)

    def write(self):
        '''Call ``write`` on each writer.
        '''
        for writer in self.writers.itervalues():
            writer.write()


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
