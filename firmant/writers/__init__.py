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


'''Writers create the filesystem to be published.

Each writer will handle a subset of the objs, and create a portion of the
outputted directory hierarchy.
'''


import abc
import collections
import logging

from firmant.chunks import AbstractChunk
from firmant.utils import class_name
from firmant import utils
from firmant.utils import workarounds


class Writer(object):
    '''Handle writing parsed objects to the filesystem.

    It is assumed that a writer will have the following methods::

        - write:  Write all objects to the filesystem.
        - write_preconditions:  Tests that the writer is able to write.  If this
          returns False, it is likely that the writer would fail.
    '''
    # TODO:  Remove prior to 0.2
    # pylint: disable-msg=R0903

    __metaclass__ = abc.ABCMeta

    def __init__(self, settings, objs, urlmapper):
        self.settings = settings
        self.objs = objs
        self.urlmapper = urlmapper
        self.log = logging.getLogger(class_name(self.__class__))

    @abc.abstractmethod
    def urls(self):
        '''A list of paths that the writer will write.

        Each path is assumed to be relative to the webroot of the blog.  It is
        implicit that paths begin with '/' (e.g. the path 'foo/bar' translates
        implies a request URI of '/foo/bar').
        '''

    @abc.abstractmethod
    def write(self):
        '''Write the objects to the filesystem.
        '''

    def write_preconditions(self):
        '''Returns true if and only if it is acceptable to proceed with writing.
        '''
        # Fail if we do not have an output directory.
        if getattr(self.settings, 'OUTPUT_DIR', None) is None:
            self.log.critical(_('``OUTPUT_DIR`` not defined in settings.'))
            return False
        return True


class WriterChunkURLs(AbstractChunk):
    '''A simple wrapper to ease the transition to chunks.
    '''
    # TODO:  Remove prior to 0.2
    # pylint: disable-msg=R0903

    def __init__(self, writer):
        super(WriterChunkURLs, self).__init__()
        self.writer = writer

    def __call__(self, environment, objects):
        newenv = environment.copy()
        newobj = objects.copy()
        newenv['urls'][class_name(self.writer.__class__)] = self.writer.urls()
        return (newenv, newobj, [WriterChunkWrite(self.writer)])

    scheduling_order = 500

class WriterChunkWrite(AbstractChunk):
    '''A simple wrapper to ease the transition to chunks.
    '''
    # TODO:  Remove prior to 0.2
    # pylint: disable-msg=R0903

    def __init__(self, writer):
        super(WriterChunkWrite, self).__init__()
        self.writer = writer

    def __call__(self, environment, objects):
        newenv = environment.copy()
        newobj = objects.copy()
        self.writer.objs = objects
        self.writer.write()
        return (newenv, newobj, [])

    scheduling_order = 900


class WriterChunk(AbstractChunk):
    '''The base writer class.

    It uses several template methods to allow the user to specify the behavior
    of the writer.  Unless otherwise mentioned, all methods and properties are
    abstract.

    In almost all cases, creating instances of this object is preferable to
    creating custom chunks to write objects.

    .. doctest::

       >>> import sys
       >>> from firmant import routing
       >>> logger = get_logger()

    .. doctest::

       >>> class SampleWriter(WriterChunk):
       ...     extension = 'txt'
       ...     def key(self, object):
       ...         return {'obj': str(object)}
       ...     def obj_list(self, environment, objects):
       ...         return objects.get('objs', [])
       ...     def render(self, environment, path, obj):
       ...         print 'Save object "%s" to "%s"' % (obj, path)
       ...
       >>> environment = {'log': logger
       ...               ,'urlmapper': urlmapper
       ...               }
       >>> environment['urlmapper'].add(
       ...     routing.SinglePathComponent('obj', str)
       ... )
       >>> objects = {'objs': ['obj1', 'obj2', 'obj3']}
       >>> sw = SampleWriter(environment, objects)
       >>> pprint(sw(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {...},
        [<firmant.writers.SampleWriter object at 0x...>,
         <firmant.writers.SampleWriter object at 0x...>])

    ..
       This shows how the implementation works, but is not meant for public
       consumption.

    .. doctest::
       :hide:

       >>> e, o, (urlwriter, preconditions) = sw(environment, objects)
       >>> pprint(urlwriter(environment, objects)) #doctest: +ELLIPSIS
       ({'log': <logging.Logger instance at 0x...>,
         'urlmapper': <firmant.routing.URLMapper object at 0x...>,
         'urls': {'firmant.writers.SampleWriter': ['http://testurl/obj1/',
                                                   'http://testurl/obj2/',
                                                   'http://testurl/obj3/']}},
        {'objs': ['obj1', 'obj2', 'obj3']},
        [])
       >>> pprint(preconditions(environment, objects)) #doctest: +ELLIPSIS
       ({...},
        {...},
        [<firmant.writers.SampleWriter object at 0x...>])
       >>> e, o, (renderer,) = preconditions(environment, objects)
       >>> renderer(environment, objects) #doctest: +ELLIPSIS
       Save object "obj1" to "outputdir/obj1/index.txt"
       Save object "obj2" to "outputdir/obj2/index.txt"
       Save object "obj3" to "outputdir/obj3/index.txt"
       ({...}, {'objs': ['obj1', 'obj2', 'obj3']}, [])

    '''

    def __init__(self, environment, objects, action=None):
        if action not in (None, 'urls', 'preconditions', 'renderer'):
            raise ValueError('`action` is invalid')
        self.__action__ = self.__default__
        if action == 'urls':
            self.__action__ = self.__urls__
        elif action == 'preconditions':
            self.__action__ = self.__preconditions__
        elif action == 'renderer':
            self.__action__ = self.__renderer__

    def __call__(self, environment, objects):
        return self.__action__(environment, objects)

    @property
    def scheduling_order(self):
        return {self.__default__: 10
               ,self.__urls__: 500
               ,self.__preconditions__: 800
               ,self.__renderer__: 900}[self.__action__]

    def __default__(self, environment, objects):
        return (environment, objects,
                [self.__class__(environment, objects, 'urls'),
                 self.__class__(environment, objects, 'preconditions')])

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

    def __preconditions__(self, environment, objects):
        for precondition in self.preconditions(environment, objects):
            if not precondition(environment, objects):
                return (environment, objects, [])
        return (environment, objects,
                [self.__class__(environment, objects, 'renderer')])

    def __renderer__(self, environment, objects):
        if 'urlmapper' not in environment:
            error = _('`urlmapper` expected in `environment`')
            environment['log'].error(error)
            return (environment, objects, [])
        urlmapper = environment['urlmapper']
        for obj in self.obj_list(environment, objects):
            path = urlmapper.path(self.extension, **self.key(obj))
            self.render(environment, path, obj)
        return (environment, objects, [])

    @property
    def writername(self):
        '''The string displayed when interacting with the user.

        This should be the name of the class they must specify in the
        configuration.  The default value should not be changed.
        '''
        return utils.class_name(self.__class__)

    @workarounds.abstractproperty
    def extension(self):
        '''The extension that will be used when finding the path/url of an
        object.

        This will be passed to a :class:`firmant.routing.URLMapper` instance.
        '''

    @workarounds.abstractmethod
    def obj_list(self, environment, objects):
        '''The objects that should be passed to :meth:`render`

        It will be passed the `environment` and `objects` dictionaries that were
        passed to the chunk.
        '''

    @workarounds.abstractmethod
    def key(self, obj):
        '''Map the object to a dictionary of attributes.

        The attributes will be passed to the :meth:`path` and :meth`url` methods
        of :class:`firmant.routing.URLMapper`.
        '''

    def preconditions(self, environment, objects):
        '''A list of callables that indicate write preconditions.

        Each callable will be passed `environment` and `objects`.  On success,
        they should return True.  On failure, they should write a message to
        `environment['log']` and return False.  It will short-circuit on
        failure.
        '''
        return []

    @workarounds.abstractmethod
    def render(self, environment, path, obj):
        '''Write the object to the path on filesystem.

        `path` will be a path under the output directory.  `obj` is one of
        the objects returned by obj_list.
        '''


def _setup(self):
    '''Setup the test cases.
    '''
    from firmant.routing import URLMapper
    self.globs['urlmapper'] = URLMapper('outputdir', 'http://testurl/')
