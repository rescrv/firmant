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


'''Copy static objects into the output directory.
'''


import os
import shutil

from firmant import writers


class StaticWriter(writers.Writer):
    '''Write copy or link the file pointed to by an object into the output
    directory.

    .. doctest::

       >>> sw = StaticWriter({}, {'static': objects.static})

    '''

    extension = None

    def key(self, static):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a static object:

            type
               This is always ``static``.

            path
               A path that describes the object relative to the input/output
               directories.

        .. doctest::
           :hide:

           >>> sw = StaticWriter({}, {'static': objects.static})

        .. doctest::

           >>> print objects.static[0].relpath
           images/88x31.png
           >>> pprint(sw.key(objects.static[0]))
           {'path': 'images/88x31.png', 'type': u'static'}

        '''
        return {'type': u'static', 'path': static.relpath}

    def obj_list(self, environment, objects):
        '''Return all objects stored under the key ``static``.

        .. doctest::
           :hide:

           >>> sw = StaticWriter({}, {'static': objects.static})

        .. doctest::

           >>> sw.obj_list(None, {})
           []
           >>> sw.obj_list(None, {'static': []})
           []
           >>> sw.obj_list(None, {'static': ['staticobj']})
           ['staticobj']

        '''
        # pylint: disable-msg=W0613
        return objects.get('static', [])

    def render(self, environment, path, static):
        '''Copy the object to the correct place on the filesystem.
        '''
        try:
            os.makedirs(os.path.dirname(path))
        except OSError, ex:
            if ex.errno != 17:
                raise
        shutil.copy2(static.fullpath, path)


def _setup(test):
    '''Setup the environment for tests.
    '''
    from testdata.chunks import c900
    test.globs['objects'] = c900
