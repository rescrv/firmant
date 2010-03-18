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


from pysettings.modules import get_module

from firmant.utils import class_name


class Firmant(object):
    '''Perform a complete run from parsing through writing.

        >>> from pysettings.settings import Settings
        >>> s = {'PARSERS': {'feeds': 'firmant.parsers.feeds.FeedParser'
        ...                 ,'posts': 'firmant.parsers.posts.PostParser'
        ...                 ,'tags': 'firmant.parsers.tags.TagParser'
        ...                 }
        ...     ,'CONTENT_ROOT': 'content'
        ...     ,'FEEDS_SUBDIR': 'feeds'
        ...     ,'POSTS_SUBDIR': 'posts'
        ...     ,'TAGS_SUBDIR': 'tags'
        ...     ,'REST_EXTENSION': 'rst'
        ...     ,'WRITERS': ['firmant.writers.j2.Jinja2PostArchiveAll'
        ...                 ,'firmant.writers.j2.Jinja2PostArchiveYearly'
        ...                 ,'firmant.writers.j2.Jinja2PostArchiveMonthly'
        ...                 ,'firmant.writers.j2.Jinja2PostArchiveDaily'
        ...                 ]
        ...     ,'POSTS_PER_PAGE': 10
        ...     ,'TEMPLATE_DIR': 'testdata/pristine/templates'
        ...     }
        >>> s = Settings(s)
        >>> f = Firmant(s)
        >>> pprint(f.parsers) #doctest: +ELLIPSIS
        {'feeds': <firmant.parsers.feeds.FeedParser object at 0x...>,
         'posts': <firmant.parsers.posts.PostParser object at 0x...>,
         'tags': <firmant.parsers.tags.TagParser object at 0x...>}
        >>> f.parse()
        >>> pprint(f.objs) #doctest: +ELLIPSIS
        {'feeds': [<firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>],
         'posts': [<firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>,
                   <firmant.parsers.RstObject object at 0x...>],
         'tags': [<firmant.parsers.RstObject object at 0x...>,
                  <firmant.parsers.RstObject object at 0x...>]}
        >>> f.setup_writers()

    '''

    def __init__(self, settings):
        self.settings = settings

        # Setup parsers
        self.parsers = dict()
        for key, parser in settings.PARSERS.items():
            mod, attr = parser.rsplit('.', 1)
            mod = get_module(mod)
            parser = getattr(mod, attr)
            self.parsers[key] = parser(self.settings)

    def parse(self):
        # Parse documents
        self.objs = dict()
        for key, parser in self.parsers.items():
            self.objs[key] = parser.parse()

    def setup_writers(self):
        '''Create instances of writer classes.
        '''
        self.writers = writers = dict()
        for writer in self.settings.WRITERS:
            mod, attr = writer.rsplit('.', 1)
            mod = get_module(mod)
            writer = getattr(mod, attr)
            # We do not retain the class name from settings as it may be the
            # case that:
            # from foo import Quux
            # really imports the class foo.bar.baz.Quux as Quux was imported
            # into the foo namespace.
            writers[class_name(writer)] = writer(self.settings, self.objs)
