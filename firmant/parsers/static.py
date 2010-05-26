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


'''Static objects are simply references to files.

The most common use for static objects is copying images and css into the proper
location in the output hierarchy.
'''


import os

from firmant import decorators
from firmant import parsers


class StaticObject(parsers.ParsedObject):
    '''An object that serves as a placeholder for a file on the filesystem.

    Attributes of :class:`StaticObject`:

        fullpath
           A path that points to the object on the filesystem.  It is possible
           to `open` or copy using `fullpath`.

        relpath
           The path relative to the root where the static objects are stored.

    .. doctest::

       >>> StaticObject(fullpath='/tmp/path/to/static/object')
       static_obj</tmp/path/to/static/object>

    '''

    # pylint: disable-msg=R0903

    __slots__ = ['fullpath', 'relpath']

    def __repr__(self):
        return 'static_obj<%s>' % getattr(self, 'fullpath', None)

    @property
    def _attributes(self):
        '''Attributes that identify a static object:

            path
               A path that describes the object relative to the input/output
               directories.

        .. doctest::

           >>> pprint(StaticObject(relpath='images/88x31.png')._attributes)
           {'path': 'images/88x31.png'}

        '''
        # pylint: disable-msg=E1101
        return {'path': self.relpath}


class StaticParser(parsers.Parser):
    '''Create stand-in objects for static files to be published.

    .. doctest::
       :hide:

       >>> environment['log'] = get_logger()

    .. doctest::

       >>> sp = StaticParser(environment, objects)
       >>> environment, objects, (parser,) = sp(environment, objects)
       >>> pprint(parser(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {'static': [static_obj<testdata/pristine/static/images/88x31.png>]},
        [])

    '''

    type = 'static'
    paths = '.*'
    cls = StaticObject

    def parse(self, environment, objects, path):
        '''Parse the object at `path` and save it under ``objects[self.type]``
        '''
        fullpath = os.path.join(self.root(environment), path)
        objects[self.type].append(self.cls(fullpath=fullpath, relpath=path))

    @decorators.in_environment('settings')
    def root(self, environment):
        '''The directory under which all static objects reside.
        '''
        settings = environment['settings']
        return os.path.join(settings.CONTENT_ROOT, settings.STATIC_SUBDIR)


def _setup(test):
    '''Setup a test environment and test set of objects.
    '''
    from pysettings.settings import Settings
    test.globs['settings'] = Settings({'CONTENT_ROOT': 'testdata/pristine'
                                      ,'STATIC_SUBDIR': 'static'
                                      })
    test.globs['environment'] = {'settings': test.globs['settings']
                                }
    test.globs['objects'] = {}
