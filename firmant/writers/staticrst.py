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


'''Render static-rest pages.
'''


from firmant import writers


class StaticRstWriter(writers.Writer):
    '''Render static-rest pages to the file system.

    :class:`StaticRstWriter` is an incomplete subclass of :class:`Writer`.  That
    is, there are still abstract methods/properties that are undefined.  In
    particular, `extension` and `render` must be defined.

    .. doctest::

       >>> class SampleStaticRstWriter(StaticRstWriter):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj):
       ...         print 'Save staticrst "%s" to "%s"' % (obj.path, path)
       ...
       >>> ssrw = SampleStaticRstWriter({}, {})
       >>> pprint(ssrw({}, {})) #doctest: +ELLIPSIS
       ({},
        {},
        [<firmant.writers.staticrst.SampleStaticRstWriter object at 0x...>,
         <firmant.writers.staticrst.SampleStaticRstWriter object at 0x...>])

    '''

    def key(self, staticrst):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a static-rest object:

            type
               This is always ``staticrst``.

            path
               A path that describes the object relative to the input/output
               directories.

        .. doctest::
           :hide:

           >>> class SampleStaticRstWriter(StaticRstWriter):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj):
           ...         print 'Save staticrst "%s" to "%s"' % (obj.path, path)
           ...
           >>> ssrw = SampleStaticRstWriter({}, {})

        .. doctest::

           >>> print objects.staticrst[0].path
           about
           >>> pprint(ssrw.key(objects.staticrst[0]))
           {'path': u'about', 'type': u'staticrst'}

        '''
        return {'type': u'staticrst', 'path': staticrst.path}

    def obj_list(self, environment, objects):
        '''Return all objects stored under the key ``staticrst``.

        .. doctest::
           :hide:

           >>> class SampleStaticRstWriter(StaticRstWriter):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj):
           ...         print 'Save staticrst "%s" to "%s"' % (obj.path, path)
           ...
           >>> ssrw = SampleStaticRstWriter({}, {})

        .. doctest::

           >>> ssrw.obj_list(None, {})
           []
           >>> ssrw.obj_list(None, {'staticrst': []})
           []
           >>> ssrw.obj_list(None, {'staticrst': ['staticobj']})
           ['staticobj']

        '''
        # pylint: disable-msg=W0613
        return objects.get('staticrst', [])


def _setup(test):
    '''Setup the environment for tests.
    '''
    from testdata.chunks import c900
    test.globs['objects'] = c900
