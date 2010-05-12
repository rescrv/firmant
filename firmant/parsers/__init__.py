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


import logging
import stat
import tempfile
import os

from docutils import io
from docutils.core import publish_programmatically
from docutils.core import Publisher

from firmant import chunks
from firmant import du
from firmant.utils import class_name
from firmant.utils import paths
from firmant.utils import workarounds
from firmant.utils.exceptions import log_uncaught_exceptions


class Parser(object):
    '''Interpret directory structures on the filesystem.

    A parser will convert a directory hierarchy on the file system into an
    internal representation that will be available to general transformation
    functions and writers.

    Example parsers include those that read posts, and those that find images.

    This class is meant to be used as a base, with the child implementing
    ``paths``, and ``parse_one``.

    The ``parse`` method is careful to trap tracebacks, and uses
    firmant.utils.exceptions.log_uncaught_exceptions to do so.

    '''

    def __init__(self, settings=None):
        '''Instantiate a Parser, bound to the settings.
        '''
        self.settings = settings
        self.log = logging.getLogger(class_name(self.__class__))

    def parse(self):
        '''Create a list of parsed objects.
        '''
        ret = list()
        for path in self.paths():
            def act():
                obj = self.parse_one(path)
                ret.append(obj)
            error = _('error parsing %s') % path
            save  = getattr(self.settings, 'SAVE_TRACEBACK', False)
            if log_uncaught_exceptions(act, self.log, error, save):
                self.log.info(_('parsed %s') % path)
        return ret

    def paths(self):
        '''Return a list of paths to objects on the file system.
        '''
        return list()

    def parse_one(self, path):
        '''Transform one path on the filesystem into a parsed object.
        '''
        return path


class ParsedObject(object):
    '''A parsed object that represents the structures on disk in a form that is
    suitable for writing.

    The constructor will accept keyword arguments to automatically fill slots.

    .. doctest::

       >>> ParsedObject(permalink='http://').permalink
       'http://'
       >>> class SampleObject(ParsedObject):
       ...     __slots__ = ['someattr']
       ...
       >>> SampleObject(someattr='value').someattr
       'value'
       >>> SampleObject(permalink='http://').permalink
       'http://'

    It is an error to provide arguments that are not in the slots of the class
    (or its base classes).

    .. doctest::

       >>> SampleObject(notinslots=True)
       Traceback (most recent call last):
       AttributeError: Excess attributes: 'notinslots'

    '''

    __slots__ = ['permalink']

    def __init__(self, **kwargs):
        slots  = [set(getattr(cls, '__slots__', []))
                  for cls in self.__class__.__mro__]
        slots  = reduce(set.union, slots)
        excess = set(kwargs.keys()) - slots
        if len(excess) > 0:
            error = _("Excess attributes: '%s'") % \
                    "', '".join(excess)
            raise AttributeError(error)
        for attr in kwargs.keys():
            setattr(self, attr, kwargs.get(attr, None))


class ChunkedParser(chunks.AbstractChunk):
    '''The base class of all chunks.

    This class defines an abstract base class that all parsers are required to
    adhere to.  To use this class in the creation of a parser, create a subclass
    with all necessary methods and properties overwritten.

    .. seealso::

       Module :mod:`abc`
          This module is part of the Python standard library in 2.6+.

    .. doctest::
       :hide:

       >>> import sys
       >>> logger = get_logger()

    To create a new type of parser, inherit from :class:`Parser`:

    .. doctest::

       >>> class SampleParser(ChunkedParser):
       ...     type = 'objs'
       ...     paths = '^numbers/[0-9]$'
       ...     def parse(self, environment, objects, path):
       ...         objects[self.type].append(str(path))
       ...     def attributes(self, environment, path):
       ...         return {'path': path}
       ...     def root(self, environment):
       ...          return 'testdata/pristine/sample'

    The new parser meets the criteria for two different abstract base classes:

    .. doctest::

       >>> import firmant.chunks
       >>> issubclass(SampleParser, firmant.chunks.AbstractChunk)
       True
       >>> issubclass(SampleParser, ChunkedParser)
       True

    .. warning::

       When creating a parser, do not store state in the parser itself.  While
       it appears that a parser is a single object, it will actually share state
       across two or more chunks during typical usage.

       If it is necessary to store state, place it in environment keyed to the
       parser class:

       .. doctest::
          :hide:

          >>> environment = {}

       .. doctest::

          >>> environment[SampleParser] = 'stored state goes here'

       This is because of the split between path selection and parsing.

    The remainder of this section is devoted to describing the implementation
    details of :class:`ChunkedParser`'s template methods.

    Chunks are passed environment and object dictionaries.  While it is not
    technically a chunk, the :class:`ChunkedParser` interface follows the same
    pattern.  When called with an environment and set of objects, a parser will
    return one more chunk (in addition to the environment and object
    dictionaries).

    .. doctest::

       >>> environment = {'log': logger
       ...               }
       >>> objects = {}
       >>> sp = SampleParser(environment, objects)
       >>> sp.scheduling_order
       10
       >>> pprint(sp(environment, objects)) #doctest: +ELLIPSIS
       ({'log': <logging.Logger instance at 0x...>},
        {},
        [<firmant.parsers.SampleParser object at 0x...>])

    .. note::

       The chunks returned do not share any state with the :class:`ChunkedParser` that
       created them.  The fact that the class name is the same is an
       implementation detail that may change in the future.

    The first chunk performs all parsing.  In the future, parsing may be broken
    into more fine-grained steps.  Right now, this is unnecessary.

    .. doctest::

       >>> environment, objects, (parse,) = sp(environment, objects)
       >>> parse.scheduling_order
       200
       >>> pprint(parse(environment, objects)) #doctest: +ELLIPSIS
       ({'log': <logging.Logger instance at 0x...>},
        {'objs': ['numbers/1', 'numbers/2', 'numbers/3']},
        [])

    ..
       These are for completeness of tests but don't contribute to docs.

    ..
       Make sure we don't accept bad actions.  This would break
       :attr:`scheduling_order` and :meth:`__call__`

    .. doctest::
       :hide:

       >>> SampleParser({}, {}, action='something else')
       Traceback (most recent call last):
       ValueError: `action` is invalid

    '''

    def __init__(self, environment, objects, action=None):
        # pylint: disable-msg=W0613
        super(ChunkedParser, self).__init__()
        if action not in (None, 'parse'):
            raise ValueError('`action` is invalid')
        self.__action__ = self.__default__
        if action == 'parse':
            self.__action__ = self.__parse__

    def __call__(self, environment, objects):
        return self.__action__(environment, objects)

    @property
    def scheduling_order(self):
        '''The following scheduling orders apply to parsers:

        10
           At timestep 10, the parser will create the chunks for finding paths
           and parsing.

        200
           Iterate over the paths in :meth:`paths` and pass each path to the
           :meth:`parse` method.  All new objects should be placed in the
           dictionary by :meth:`parse`.

        '''
        return {self.__default__: 10
               ,self.__parse__: 200}[self.__action__]

    def __default__(self, environment, objects):
        return (environment, objects,
                [self.__class__(environment, objects, 'parse')])

    def __parse__(self, environment, objects):
        for path in sorted(paths.recursive_listdir(self.root(environment),
            matches=self.paths)):
            if self.type not in objects:
                objects[self.type] = []
            self.parse(environment, objects, path)
        return environment, objects, []

    @workarounds.abstractproperty
    def paths(self):
        '''Determine which paths should be parsed.

        This is a regular expression that will be used to match pathnames
        relative to :meth:`root`.
        '''

    @workarounds.abstractmethod
    def parse(self, environment, objects, path):
        '''Parse the object at path.

        Any new objects that are created during the parsing of the object at
        path should be added directly to the objects dictionary (this includes
        the parsed object itself).
        '''

    @workarounds.abstractmethod
    def attributes(self, environment, path):
        '''The dict of attributes that define permalink of the object at path.

        The permalink will be derived from these attributes by passing them to
        a :class:`firmant.routing.URLMapper`.

        Passing only `path` and not the parsed object is intended to force
        objects on the filesystem to be unique.  It's entirely possible to make
        two paths on the filesystem have the same set of attributes; try to
        avoid this.

        '''

    @workarounds.abstractproperty
    def type(self):
        '''The type of the primary object to be parsed (e.g. ``posts``).

        Parsed objects will be added to the objects dictionary under this key.

        This value has no impact on secondary objects that are generated (e.g.
        objects that are created from embedded LaTeX equations).
        '''

    @workarounds.abstractmethod
    def root(self, environment):
        '''The root under which all objects to be parsed by this parser reside.
        '''


class ChunkedRstParser(ChunkedParser):
    '''A parser containing common functionality for parsing reStructuredTest.
    '''

    def parse(self, environment, objects, path):
        '''Parse the reStructuredText doc at `path` and pass the relevant pieces
        to :meth:`rstparse`.
        '''
        metadata = {}
        transforms = [du.meta_data_transform(metadata)]
        pub = du.publish(path, transforms)
        pieces = {}
        pieces['metadata'] = metadata
        pieces['document'] = pub.document
        pieces['pub_parts'] = pub.writer.parts
        self.rstparse(environment, objects, path, pieces)

    @workarounds.abstractproperty
    def cls(self):
        '''The class object that should be used for new parsed objects.
        '''

    @workarounds.abstractmethod
    def rstparse(self, environment, objects, path, pieces):
        '''The main method to override when creating new reStructuredText
        parsers.

        The `pieces` dictionary contains the following keys:

        metadata
           All pieces of metadata pulled from the document using
           :func:`firmant.du.meta_data_transform`.

        pub_parts
           The pieces returned by the html writer.

        document
           The actual doctree of that was produced as a result of parsing, and
           applying transformations.

        '''
        # TODO figure out how to handle transforms later (by deferring
        # attributes derived from pub_parts).


class RstObject(object):
    '''An object representing a parsed restructured text document.
    '''


class RstParser(Parser):
    '''Interpret *.rst for a given directory.

    For each reSt document, parse it to a doctree and extract its metadata.
    '''

    auto_metadata = []
    '''Attributes which should be automatically read from metadata.

    This value should be a list of 2-tuples where the first value is the
    attribute on the entry, and the second is the key to the metadata
    dictionary.
    '''

    auto_pubparts = []
    '''Attributes which should be automatically read from publisher parts.

    This value should be a list of 2-tuples where the first value is the
    attribute on the entry, and the second is the key to the publisher's parts
    dictionary.
    '''

    def new_object(self, path, d, pub):
        '''Return an instance of the object to which rst documents are parsed.
        '''
        return RstObject()

    def default(self, attr):
        '''Return the default value of an attribute.

        This base class version is limited::

            >>> r = RstParser()
            >>> r.default('foo') is None
            True

        It is intended that this function will be overridden (possibly to read
        from settings).

        '''
        return None

    def post_process(self, doc):
        '''Post-process the document.
        '''

    def parse_one(self, path):
        '''Transform one path on the filesystem into a parsed object.
        '''
        d = dict()
        transforms = [du.meta_data_transform(d)]
        pub = du.publish(path, transforms)

        # Create a new object, using information from path and dictionary to
        # fill in all values not filled by auto_metadata or the defaults.
        o = self.new_object(path, d, pub)

        # Automatically assign all auto_metadata to new object.
        for attr, directive in self.auto_metadata:
            default = self.default(attr)
            val = d.get(directive, None) or default
            setattr(o, attr, val)

        # Automatically assign all auto_pubparts to new object.
        for attr, directive in self.auto_pubparts:
            default = self.default(attr)
            val = pub.writer.parts.get(directive, None) or default
            setattr(o, attr, val)

        # Save the doctree for future use.
        o.document = pub.document

        # Post process the document.
        self.post_process(o)

        return o
