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


'''StaticRst objects (also known as "flatpages")  provide for free-form page
layouts.
'''


import os

from firmant import decorators
from firmant import parsers


class StaticRstObject(parsers.RstParsedObject):
    '''A static object that contains title, content, and path information.

    The difference between this class and
    :class:`firmant.parsers.static.StaticObject` is this class is parsed from
    a restructured text document while the other is only from filesystem
    information.

    Attributes of :class:`StaticRstObject`:

        title
           The title from the parsed restructured text document.

        path
           The path relative to the root where the static objects are stored.

        content
           The content of the restructured text document.  This includes the
           title and subtitle components from the docutils writer.

    .. doctest::

       >>> StaticRstObject(path='projects/firmant')
       staticrst_obj<projects/firmant>

    '''

    # pylint: disable-msg=R0903

    __slots__ = ['path']

    _pubparts = [('content', 'html_body')
                   ,('title', 'title')
                   ]

    def __repr__(self):
        return 'staticrst_obj<%s>' % getattr(self, 'path', None)

    @property
    def _attributes(self):
        '''Attributes that identify a static object:

            path
               A path that describes the object relative to the input/output
               directories.

        .. doctest::

           >>> pprint(StaticRstObject(path='about/projects/firmant')._attributes)
           {'path': 'about/projects/firmant'}

        '''
        # pylint: disable-msg=E1101
        return {'path': self.path}


class StaticRstParser(parsers.RstParser):
    '''Create a static page from reStructured Text.

    .. doctest::
       :hide:

       >>> environment['log'] = get_logger()

    .. doctest::

       >>> srp = StaticRstParser(environment, objects)
       >>> environment, objects, (parser,) = srp(environment, objects)
       >>> pprint(parser(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {'staticrst': [staticrst_obj<about>,
                       staticrst_obj<empty>,
                       staticrst_obj<links>]},
        [])

    '''

    type = 'staticrst'
    paths = '.*\.rst'
    cls = StaticRstObject

    @decorators.in_environment('settings')
    def root(self, environment):
        '''The directory under which all staticrst objects reside.
        '''
        settings = environment['settings']
        return os.path.join(settings.CONTENT_ROOT, settings.STATIC_RST_SUBDIR)

    def rstparse(self, environment, objects, path, pieces):
        '''Use the parsed rst document to construct the necessary objects.
        '''
        attrs = {}
        attrs['path'] = unicode(path[:-4])
        attrs['_pub'] = pieces['pub']
        objects[self.type].append(self.cls(**attrs))


def _setup(test):
    '''Setup the tests.
    '''
    from pysettings.settings import Settings
    from firmant import routing
    test.globs['settings'] = Settings({'CONTENT_ROOT': 'testdata/pristine'
                                      ,'STATIC_RST_SUBDIR': 'flat'
                                      })
    urlmapper = routing.URLMapper('/path/to/output/dir', 'http://testurl/', [])
    test.globs['environment'] = {'settings': test.globs['settings']
                                ,'urlmapper': urlmapper
                                }
    test.globs['objects'] = {}
