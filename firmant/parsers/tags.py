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


'''Manipulate tag objects for Firmant.
'''


import os

from firmant import decorators
from firmant import parsers


class Tag(parsers.RstParsedObject):
    '''A tag is a means of categorizing objects.

    Attributes of :class:`Tag`:

        slug
           A unique string that identifies the tag.

        title
           A longer title used for identifying the tag to the user.

        subtitle
           An even longer description of the tag that may be displayed to the
           user in combination with `title`.

        content
           The content of the restructured text document.  This does not include
           the title information.

        posts
           A list of cross-referenced posts.  This will be blank until
           cross-referencing happens at a later point in time.

    .. note::

       All string attributes except `slug` may be ``''``.  Posts will be ``[]``
       until the cross-referencing chunk happens.

    .. doctest::

       >>> Tag(slug='foo')
       Tag(foo)

    '''

    # pylint: disable-msg=R0903

    __slots__ = ['slug', 'posts']

    _pubparts = [('content', 'fragment')
                   ,('title', 'title')
                   ,('subtitle', 'subtitle')
                   ]

    def __repr__(self):
        return 'Tag(%s)' % getattr(self, 'slug', None)

    @property
    def _attributes(self):
        '''Attributes that identify a tag object:

            slug
               The `slug` attribute of the :class:`Tag` object.

        .. doctest::

           >>> pprint(Tag(slug='firmantstuff')._attributes)
           {'slug': 'firmantstuff'}

        '''
        # We remove the 'rst' extension
        # pylint: disable-msg=E1101
        return {'slug': self.slug}


class TagParser(parsers.RstParser):
    r'''Parse all tags matching ``[-a-zA-Z0-9_.]+``.

    .. doctest::
       :hide:

       >>> environment['log'] = get_logger()

    .. doctest::

       >>> tp = TagParser(environment, objects)
       >>> environment, objects, (parser,) = tp(environment, objects)
       >>> pprint(parser(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {'tag': [Tag(bar), Tag(baz), Tag(foo), Tag(quux)]},
        [])

    '''

    type = 'tag'
    paths = '^[-a-zA-Z0-9_.]+\.rst$'
    cls = Tag

    @decorators.in_environment('settings')
    def root(self, environment):
        '''The directory under which all tag objects reside.
        '''
        settings = environment['settings']
        return os.path.join(settings.CONTENT_ROOT, settings.TAGS_SUBDIR)

    def rstparse(self, environment, objects, path, pieces):
        '''Use the parsed rst document to construct the necessary objects.
        '''
        attrs = {}
        attrs['slug'] = unicode(path[:-4])
        attrs['_pub'] = pieces['pub']
        objects[self.type].append(self.cls(**attrs))


def _setup(test):
    '''Setup the tests.
    '''
    from pysettings.settings import Settings
    from firmant import routing
    test.globs['settings'] = Settings({'CONTENT_ROOT': 'testdata/pristine'
                                      ,'TAGS_SUBDIR': 'tags'
                                      })
    urlmapper = routing.URLMapper('/path/to/output/dir', 'http://testurl/', [])
    test.globs['environment'] = {'settings': test.globs['settings']
                                ,'urlmapper': urlmapper
                                }
    test.globs['objects'] = {}
