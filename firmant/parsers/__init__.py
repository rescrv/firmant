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

from firmant.du import MetaDataStandaloneReader
from firmant.i18n import _
from firmant.utils import class_name


__all__ = ['Parser']


class Parser(object):
    '''Interpret directory structures on the filesystem.

    A parser will convert a directory hierarchy on the file system into an
    internal representation that will be available to general transformation
    functions and writers.

    Example parsers include those that read posts, and those that find images.

    This class is meant to be used as a base, with the child implementing
    ``paths``, and ``parse_one``.

    The ``parse`` method is careful to trap tracebacks.  For example, if
    parse_one throws an exception, and the setting ``SAVE_TRACEBACK`` is False::

        >>> from pysettings.settings import Settings
        >>> class BadParser(Parser):
        ...     def parse_one(self, path): raise RuntimeError('bad')
        ...     def paths(self): return [1]
        >>> bp = BadParser(Settings(SAVE_TRACEBACK=False))
        >>> bp.log = Mock('log')
        >>> bp.parse()
        Called log.error('error parsing 1')
        Called log.info('traceback not saved')
        []

    With SAVE_TRACEBACK enabled, it will save to a file using tempfile.mkstemp.

    If an exception is thrown while saving to the file, it will warn about
    the potential for infinite recursion and stop::

        >>> from minimock import restore
        >>> import tempfile
        >>> tempfile.mkstemp = Mock('mkstemp')
        >>> tempfile.mkstemp.mock_raises = ValueError
        >>> bp = BadParser(Settings(SAVE_TRACEBACK=True))
        >>> bp.log = Mock('log')
        >>> bp.parse()
        Called log.error('error parsing 1')
        Called mkstemp(prefix='firmant', text=True)
        Called log.error("it's turtles all the way down")
        []
        >>> restore()

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
            try:
                obj = self.parse_one(path)
                ret.append(obj)
            except:
                import traceback
                self.log.error(_('error parsing %s') % path)
                if getattr(self.settings, 'SAVE_TRACEBACK', False):
                    try:
                        t, path = tempfile.mkstemp(prefix='firmant', text=True)
                        traceback.print_exc(file=t)
                        t.flush()
                        t.close()
                        self.log.error(_('traceback saved to %s') % path)
                    except:
                        self.log.error(_("it's turtles all the way down"))
                else:
                    self.log.info(_('traceback not saved'))
            else:
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
        args = {'source': None
               ,'source_path': path
               ,'source_class': io.FileInput
               ,'destination_class': io.StringOutput
               ,'destination': None
               ,'destination_path': None
               ,'reader': MetaDataStandaloneReader(data=d), 'reader_name': None
               ,'parser': None, 'parser_name': 'restructuredtext'
               ,'writer': None, 'writer_name': 'html'
               ,'settings': None, 'settings_spec': None
               ,'settings_overrides': None
               ,'config_section': None
               ,'enable_exit_status': None
               }
        null, pub = publish_programmatically(**args)

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
