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

from firmant import utils
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
        >>> f()
        >>> pprint(f.objs) #doctest: +ELLIPSIS
        {'feed': [Feed(bar), Feed(baz), Feed(foo), Feed(quux)],
         'post': [Post(2009-12-31-party),
                  Post(2010-01-01-newyear),
                  Post(2010-02-01-newmonth),
                  Post(2010-02-02-newday),
                  Post(2010-02-02-newday2)],
         'static': [static_obj<testdata/pristine/static/images/88x31.png>],
         'staticrst': [staticrst_obj<about>,
                       staticrst_obj<empty>,
                       staticrst_obj<links>],
         'tag': [Tag(bar), Tag(baz), Tag(foo), Tag(quux)]}

    '''

    # pylint: disable-msg=R0903

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
        self.chunks.append(CreatePermalinks())
        self.chunks.append(CrossReference())

        for glob in settings.GLOBALS:
            glob = utils.get_obj(glob)
            self.chunks.append(glob(self.env, self.objs))

        # Setup parsers
        for parser in settings.PARSERS.values():
            parser = utils.get_obj(parser)
            if issubclass(parser, AbstractChunk):
                self.chunks.append(parser(self.env, self.objs))
            else:
                self.log.error(_("'%s' is not a parser.") % str(parser))

        # Setup writers
        for writer in self.settings.WRITERS:
            writer = utils.get_obj(writer)
            self.chunks.append(writer(self.env, self.objs))

    def __call__(self):
        while len(self.chunks):
            self.chunks.sort(key = lambda x: x.scheduling_order)
            chunk = self.chunks[0]
            self.env, self.objs, newchunks = chunk(self.env, self.objs)
            self.chunks = self.chunks[1:]
            for newchunk in newchunks:
                if newchunk.scheduling_order <= chunk.scheduling_order:
                    error = _('New chunk violates scheduling_order constraint')
                    self.log.error(error)
                else:
                    self.chunks.append(newchunk)


class CrossReference(AbstractChunk):
    '''A chunk that cross-references posts/tags/feeds.
    '''

    # TODO improve this to do arbitrary cross-references.
    # pylint: disable-msg=R0903

    def __call__(self, environment, objects):
        '''Cross reference tags and feeds
        '''
        # pylint: disable-msg=R0912
        for feed in objects.get('feed', []):
            feed.posts = list()
        for tag in objects.get('tag', []):
            tag.posts = list()
        for post in objects.get('post', []):
            to_delete = list()
            for i, ptag in enumerate(post.tags):
                seen = False
                for tag in objects.get('tag', []):
                    if tag.slug == ptag:
                        seen = True
                        tag.posts.append(post)
                        post.tags[i] = tag
                if not seen:
                    warning  = _("Tag '%s' referenced but not defined.")
                    warning %= ptag
                    environment['log'].warning(warning)
                    to_delete.append(i)
            for i in reversed(to_delete):
                del post.tags[i]
            to_delete = list()
            for i, pfeed in enumerate(post.feeds):
                seen = False
                for feed in objects.get('feed', []):
                    if feed.slug == pfeed:
                        seen = True
                        feed.posts.append(post)
                        post.feeds[i] = feed
                if not seen:
                    error  = _("Feed '%s' referenced but not defined.")
                    error %= pfeed
                    environment['log'].error(error)
                    to_delete.append(i)
            for i in reversed(to_delete):
                del post.feeds[i]
        return (environment, objects, [])

    scheduling_order = 700


class CheckURLConflicts(AbstractChunk):
    '''A chunk that warns of writers with conflicting URLs.
    '''

    # pylint: disable-msg=R0903

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


class CreatePermalinks(AbstractChunk):
    '''For objects that declare attributes, add a permalink.

    Pre-existing permalinks will not be overwritten.

    '''

    # pylint: disable-msg=R0903

    def __call__(self, environment, objects):
        if 'settings' not in environment:
            environment['log'].error(_('Expected `settings` in environment.'))
            return
        if 'urlmapper' not in environment:
            environment['log'].error(_('Expected `urlmapper` in environment.'))
            return
        settings = environment['settings']
        urlmapper = environment['urlmapper']
        for typ, objlist in objects.items():
            for obj in objlist:
                if hasattr(obj, '_attributes') \
                        and (not hasattr(obj, 'permalink')
                             or obj.permalink is None):
                    # pylint: disable-msg=W0212
                    attrs = obj._attributes
                    attrs['type'] = typ
                    extension = settings.PERMALINK_EXTENSIONS[typ]
                    obj.permalink = urlmapper.url(extension, **attrs)
        return (environment, objects, [])

    scheduling_order = 300


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
