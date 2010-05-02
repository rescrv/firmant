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


class WriterChunk(object):
    '''A chunk that makes it easy to create a writer.

    This class handles creating chunks that will be scheduled correctly.  All
    that is necessary is to provide:

    `writername`
        The name, as it will be displayed to the user.  This should be the name
        of the class they must specify in the settings file to include the
        :class:`WriterChunk`.

    `extension`
        The extension that will be used when writing files out.  This will be
        passed to a :class:`firmant.routing.URLMapper` instance.

    `obj_list`
        A callable that will return a list of objects to pass to `render`.  It
        will be passed the `environment` and `objects` dictionaries passed to
        the chunk.

    `key`
        A callable that returns a dictionary of attributes that should be passed
        to the :class:`firmant.routing.URLMapper`'s :meth:`url` and :meth:`path`
        methods.

    `preconditions`
        An iterable of callables that return booleans indicating success of
        write preconditions.  These will be passed `environment` and `objects`.
        On success, they should return True.  On failure, they should write a
        message to `environment['log']` and return False.  It will short-circuit
        on failure.

    `render`
        A callable that accepts the environment, the path to which it should
        write, and an object that should be written.  The object to be written
        is in the same form returned by the `obj_list` callable.

    In almost all cases, creating instances of this object is preferable to
    creating custom chunks to write objects.

    '''

    # pylint: disable-msg=R0913
    # pylint: disable-msg=R0903

    def __init__(self, writername, extension, obj_list, key, preconditions,
            render):
        super(WriterChunk, self).__init__()
        self.__writername__ = writername
        self.__extension__ = extension
        self.__obj_list__ = obj_list
        self.__key__ = key
        self.__preconditions__ = preconditions
        self.__render__ = render

    def __call__(self, environment, objects):
        return (environment, objects,
                [WriterURLs(self.__writername__, self.__extension__,
                    self.__obj_list__, self.__key__, self.__preconditions__,
                    self.__render__)])

    scheduling_order = 0


class WriterURLs(AbstractChunk):
    '''An internal class used by :class:`WriterChunk`.

    You should never find it necessary to interact with this class.  It should
    be considered an implementation detail, and not part of the public API.

    This class checks that every precondition specified returns true.

    '''

    # pylint: disable-msg=R0913
    # pylint: disable-msg=R0903

    def __init__(self, writername, extension, obj_list, key, preconditions,
            render):
        super(WriterURLs, self).__init__()
        self.__writername__ = writername
        self.__extension__ = extension
        self.__obj_list__ = obj_list
        self.__key__ = key
        self.__preconditions__ = preconditions
        self.__render__ = render

    def __call__(self, environment, objects):
        if 'urls' not in environment:
            error = _('`urls` expected in `environment`')
            environment['log'].error(error)
            return
        if 'urlmapper' not in environment:
            error = _('`urlmapper` expected in `environment`')
            environment['log'].error(error)
            return
        urlmapper = environment['urlmapper']
        newenv = environment.copy()
        newenv['urls'][self.__writername__] = ret = []
        for obj in self.__obj_list__(environment, objects):
            url = urlmapper.url(self.__extension__, **self.__key__(obj))
            ret.append(url)
        ret.sort()
        return (newenv, objects, [])

    scheduling_order = 500


class WriterPreconditions(AbstractChunk):
    '''An internal class used by :class:`WriterChunk`.

    You should never find it necessary to interact with this class.  It should
    be considered an implementation detail, and not part of the public API.

    It will check all of the write preconditions.

    '''

    # pylint: disable-msg=R0913
    # pylint: disable-msg=R0903

    def __init__(self, writername, extension, obj_list, key, preconditions,
            render):
        super(WriterPreconditions, self).__init__()
        self.__writername__ = writername
        self.__extension__ = extension
        self.__obj_list__ = obj_list
        self.__key__ = key
        self.__preconditions__ = preconditions
        self.__render__ = render

    def __call__(self, environment, objects):
        for precondition in self.__preconditions__:
            if not precondition(environment, objects):
                return (environment, objects, [])
        return (environment, objects,
                [WriterWrite(self.__writername__, self.__extension__,
                    self.__obj_list__, self.__key__, self.__preconditions__,
                    self.__render__)])


class WriterWrite(AbstractChunk):
    '''An internal class used by :class:`WriterChunk`.

    You should never find it necessary to interact with this class.  It should
    be considered an implementation detail, and not part of the public API.

    It will call the `render` function with the objects returned by the callable
    `obj_list`.

    This class will be used as a chunk that follows from chunks created by
    :class:`WriterChunk`.

    .. doctest::
       :hide:

       >>> from firmant import routing
       >>> logger = get_logger()

    .. doctest::

       >>> writername = 'SampleWriter'
       >>> extension = 'txt'
       >>> obj_list = lambda e, o: o['objs']
       >>> key = lambda o: {'obj': o}
       >>> preconditions = None
       >>> def render(environment, path, objects):
       ...     print 'Save object "%s" to "%s"' % (objects, path)
       ...
       >>> environment = {'log': logger
       ...               ,'urlmapper': urlmapper
       ...               }
       >>> environment['urlmapper'].add(
       ...     routing.SinglePathComponent('obj', str)
       ... )
       >>> ww = WriterWrite(writername, extension, obj_list,
       ...                  key, preconditions, render)
       >>> ww(environment, {'objs': ['obj1', 'obj2', 'obj3']}) #doctest: +ELLIPSIS
       Save object "obj1" to "outputdir/obj1/index.txt"
       Save object "obj2" to "outputdir/obj2/index.txt"
       Save object "obj3" to "outputdir/obj3/index.txt"
       ({...}, {'objs': ['obj1', 'obj2', 'obj3']}, [])

    .. note::

       :meth:`__call__` expects a :class:`firmant.routing.URLMapper` to be in
       the environment and will generate an error if there is not.  It will log
       to the logger in the error case.

       .. doctest::

          >>> ww({'log': logger}, {}) #doctest: +ELLIPSIS
          [ERROR] `urlmapper` expected in `environment`
          ({'log': <logging.Logger instance at 0x...>}, {}, [])

    '''

    # pylint: disable-msg=R0913
    # pylint: disable-msg=R0903

    def __init__(self, writername, extension, obj_list, key, preconditions,
            render):
        super(WriterWrite, self).__init__()
        self.__writername__ = writername
        self.__extension__ = extension
        self.__obj_list__ = obj_list
        self.__key__ = key
        self.__preconditions__ = preconditions
        self.__render__ = render

    def __call__(self, environment, objects):
        if 'urlmapper' not in environment:
            error = _('`urlmapper` expected in `environment`')
            environment['log'].error(error)
            return (environment, objects, [])
        urlmapper = environment['urlmapper']
        for obj in self.__obj_list__(environment, objects):
            path = urlmapper.path(self.__extension__, **self.__key__(obj))
            self.__render__(environment, path, obj)
        return (environment, objects, [])

    scheduling_order = 900


def _setup(self):
    '''Setup the test cases.
    '''
    from firmant.routing import URLMapper
    self.globs['urlmapper'] = URLMapper('outputdir', 'http://testurl/')
