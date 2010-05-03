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


'''Writers transform parsed objects into files and directories on disk.

Writers are implemented behind the scenes in terms of chunks as defined in
:mod:`firmant.chunks`.  This is because writers need to do work at two different
points in time, with other chunks being scheduled in between.  The first chunk
executed by a writer will forward-declare URLs that the writer claims
responsibility for.  The second chunk renders objects and saves the result to
disk.

Modules in this package:

.. autosummary::
   :toctree: ../generated

   static
   staticrst

'''


from firmant import chunks
from firmant import utils
from firmant.utils import workarounds


class Writer(chunks.AbstractChunk):
    '''The base class of all writers.

    This class defines an abstract base class that all writers are required to
    adhere to.  To use this class in the creation of a writer, create a subclass
    with all necessary methods and properties overwritten.

    .. seealso::

       Module :mod:`abc`
          This module is part of the Python standard library in 2.6+.

    .. doctest::
       :hide:

       >>> import sys
       >>> from firmant import routing
       >>> logger = get_logger()

    To create a new type of writer, inherit from :class:`Writer`: 

    .. doctest::

       >>> class SampleWriter(Writer):
       ...     extension = 'txt'
       ...     def key(self, obj):
       ...         return {'obj': str(obj)}
       ...     def obj_list(self, environment, objects):
       ...         return objects.get('objs', [])
       ...     def render(self, environment, path, obj):
       ...         print 'Save object "%s" to "%s"' % (obj, path)

    The new writer meets the criteria for two different abstract base classes:

    .. doctest::

       >>> import firmant.chunks
       >>> issubclass(SampleWriter, firmant.chunks.AbstractChunk)
       True
       >>> issubclass(SampleWriter, Writer)
       True

    .. warning::

       When creating a writer, do not store state in the writer itself.  While
       it appears that a writer is a single object, it will actually share state
       across three or more chunks during typical usage.

       If it is necessary to store state, place it in environment keyed to the
       writer class:

       .. doctest::
          :hide:

          >>> environment = {}

       .. doctest::

          >>> environment[SampleWriter] = 'stored state goes here'

       This is because of the need to split actions between url
       forward-declaration and rendering.

    The remainder of this section is devoted to describing the implementation
    details of :class:`Writer`'s template methods.

    Chunks are passed environment and object dictionaries.  While it is not
    technically a chunk, the :class:`Writer` interface follows the same pattern.
    When called with an environment and set of objects, a writer will return two
    more chunks (in addition to the environment and object dictionaries).

    .. doctest::

       >>> environment = {'log': logger
       ...               ,'urlmapper': urlmapper
       ...               }
       >>> environment['urlmapper'].add(
       ...     routing.SinglePathComponent('obj', str)
       ... )
       >>> objects = {'objs': ['obj1', 'obj2', 'obj3']} 
       >>> sw = SampleWriter(environment, objects)
       >>> sw.scheduling_order
       10
       >>> pprint(sw(environment, objects)) #doctest: +ELLIPSIS
       ({'log': <logging.Logger instance at 0x...>,
         'urlmapper': <firmant.routing.URLMapper object at 0x...>},
        {'objs': ['obj1', 'obj2', 'obj3']},
        [<firmant.writers.SampleWriter object at 0x...>,
         <firmant.writers.SampleWriter object at 0x...>])

    .. note::

       The chunks returned do not share any state with the :class:`Writer` that
       created them.  The fact that the class name is the same is an
       implementation detail that may change in the future.

    The first chunk is the chunk that will build the urls, while the second is
    used for rendering.  Neither chunk returns more chunks.

    .. doctest::

       >>> environment, objects, (urls, render) = sw(environment, objects)
       >>> urls.scheduling_order
       500
       >>> render.scheduling_order
       900
       >>> pprint(urls(environment, objects)) #doctest: +ELLIPSIS
       ({'log': <logging.Logger instance at 0x...>,
         'urlmapper': <firmant.routing.URLMapper object at 0x...>,
         'urls': {'firmant.writers.SampleWriter': ['http://testurl/obj1/',
                                                   'http://testurl/obj2/',
                                                   'http://testurl/obj3/']}},
        {'objs': ['obj1', 'obj2', 'obj3']},
        [])
       >>> pprint(render(environment, objects)) #doctest: +ELLIPSIS
       Save object "obj1" to "outputdir/obj1/index.txt"
       Save object "obj2" to "outputdir/obj2/index.txt"
       Save object "obj3" to "outputdir/obj3/index.txt"
       ({'log': <logging.Logger instance at 0x...>,
         'urlmapper': <firmant.routing.URLMapper object at 0x...>},
        {'objs': ['obj1', 'obj2', 'obj3']},
        [])

    ..
       These are for completeness of tests but don't contribute to docs.

    ..
       Make sure we don't accept bad actions.  This would break
       :attr:`scheduling_order` and :meth:`__call__`

    .. doctest::
       :hide:

       >>> SampleWriter({}, {}, action='something else')
       Traceback (most recent call last):
       ValueError: `action` is invalid

    ..
       Test the failure case for verifying that a urlmapper exists in the
       environment.

    .. doctest::

       >>> SampleWriter({}, {}, action='urls')({}, {})
       Traceback (most recent call last):
       ValueError: `urlmapper` expected in `environment`
       >>> SampleWriter({}, {}, action='renderer')({}, {})
       Traceback (most recent call last):
       ValueError: `urlmapper` expected in `environment`

    '''

    def __init__(self, environment, objects, action=None):
        # pylint: disable-msg=W0613
        super(Writer, self).__init__()
        if action not in (None, 'urls', 'renderer'):
            raise ValueError('`action` is invalid')
        self.__action__ = self.__default__
        if action == 'urls':
            self.__action__ = self.__urls__
        elif action == 'renderer':
            self.__action__ = self.__renderer__

    def __call__(self, environment, objects):
        return self.__action__(environment, objects)

    @property
    def scheduling_order(self):
        '''The following scheduling orders apply to writers:

        10
           At timestep 10, the writer will create the chunks for forward
           declaration and rendering.

        500
           At timestep 500, the writer will forward-declare urls.

        900
           At timestep 900, the writer will render the objects.
        '''
        return {self.__default__: 10
               ,self.__urls__: 500
               ,self.__renderer__: 900}[self.__action__]

    def __default__(self, environment, objects):
        return (environment, objects,
                [self.__class__(environment, objects, 'urls'),
                 self.__class__(environment, objects, 'renderer')])

    def __urls__(self, environment, objects):
        if 'urlmapper' not in environment:
            error = _('`urlmapper` expected in `environment`')
            raise ValueError(error)
        urlmapper = environment['urlmapper']
        newenv = environment.copy()
        if 'urls' not in newenv:
            newenv['urls'] = {}
        newenv['urls'][self.writername] = ret = []
        for obj in self.obj_list(environment, objects):
            url = urlmapper.url(self.extension, **self.key(obj))
            ret.append(url)
        ret.sort()
        return (newenv, objects, [])

    def __renderer__(self, environment, objects):
        if 'urlmapper' not in environment:
            error = _('`urlmapper` expected in `environment`')
            raise ValueError(error)
        urlmapper = environment['urlmapper']
        for obj in self.obj_list(environment, objects):
            path = urlmapper.path(self.extension, **self.key(obj))
            self.render(environment, path, obj)
        return (environment, objects, [])

    @workarounds.abstractproperty
    def extension(self):
        '''The extension that will be used when finding the path/url of an
        object.

        This will be passed to a :class:`firmant.routing.URLMapper` instance.
        '''

    @workarounds.abstractmethod
    def key(self, obj):
        '''Map the object to a dictionary of attributes.

        The attributes will be passed to the :meth:`path` and :meth`url` methods
        of :class:`firmant.routing.URLMapper`.
        '''

    @workarounds.abstractmethod
    def obj_list(self, environment, objects):
        '''The objects that should be passed to :meth:`render`

        It will be passed the `environment` and `objects` dictionaries that were
        passed to the chunk.
        '''

    @workarounds.abstractmethod
    def render(self, environment, path, obj):
        '''Write the object to the path on filesystem.

        `path` will be a path under the output directory.  `obj` is one of
        the objects returned by obj_list.
        '''

    @property
    def writername(self):
        '''The string displayed when interacting with the user.

        This should be the name of the class they must specify in the
        configuration.  The default value should not be changed.
        '''
        return utils.class_name(self.__class__)


def _setup(self):
    '''Setup the test cases.
    '''
    from firmant.routing import URLMapper
    self.globs['urlmapper'] = URLMapper('outputdir', 'http://testurl/')
