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


'''Functions for interacting with the docutils module.
'''


__all__ = ['Copyright', 'publish_parts_doc']


import datetime

from docutils.transforms.components import Filter
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.core import publish_programmatically
from docutils import io
from docutils import nodes


def meta_data_directive(func, transform=Filter, whitespace=False):
    '''Create a Directive class to store data to a pending node.

    The function ``func`` is passed the contents of the node and a dictionary
    into which it should place all relevant metadata it extracts from the
    contents.
    '''

    class MetaDataDirective(Directive):
        '''A generic directive for capturing metadata.
        '''

        required_arguments = 0
        optional_arguments = 0
        final_argument_whitespace = whitespace
        option_spec = dict()
        has_content = True

        def run(self):
            # Raise an error if the directive does not have contents.
            self.assert_has_content()

            # Parse the contents into metadata.
            d = dict()
            try:
                func(d, self.content)
            except ValueError, e:
                error = self.state_machine.reporter.error(str(e))
                return []

            # Insert a pending node with the metadata.
            pending = nodes.pending(transform, details=d)
            pending.details.update({'component': 'reader', 'format': 'html'})
            self.state.document.note_pending(pending)

            # TODO: Remove this block
            # This block is here to facilitate moving the old directive classes
            # to use MetaDataDirective without requiring changes to the parsing
            # process.
            doc = self.state.document
            for key, val in d.items():
                try:
                    iter(val)
                    if hasattr(doc, key):
                        val = getattr(doc, key) + val
                except TypeError:
                    pass
                setattr(doc, key, val)

            return [pending]

    return MetaDataDirective


def copyright(d, content):
    r'''Interpret the content as a copyright declaration.

        >>> d = dict()
        >>> copyright(d, [u'foo', u'bar'])
        >>> d['copyright']
        u'foo\nbar'

    '''
    d['copyright'] = '\n'.join(content)


class Time(Directive):
    '''A restructured text directive for time information.
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        try:
            dt = datetime.datetime.strptime(''.join(self.content), '%H:%M')
        except ValueError:
            error = self.state_machine.reporter.error(
                    'Invalid time format:  the %H:%M format should be used.')
            return [error]
        self.state.document.time = dt.time()
        return []


class Timezone(Directive):
    '''A restructured text directive for timezone information.
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        text = ''.join(self.content)
        self.state.document.timezone = text
        return []


class Author(Directive):
    '''A restructured text directive for author information.
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        text = ''.join(self.content)
        self.state.document.author = text
        return []


class Updated(Directive):
    '''A restructured text directive for updated timestamps
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        try:
            dt = datetime.datetime.strptime(''.join(self.content), '%Y-%m-%d %H:%M')
        except ValueError:
            error = self.state_machine.reporter.error(
                    'Invalid time format:  the %Y-%m-%d %H:%M format should be used.')
            return [error]
        self.state.document.updated = dt
        return []


class Tag(Directive):
    '''A restructured text directive for tag information.
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        text = ''.join(self.content)
        if not hasattr(self.state.document, 'tags'):
            self.state.document.tags = list()
        self.state.document.tags.append(text)
        return []


class Feed(Directive):
    '''A restructured text directive for tag information.
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        text = ''.join(self.content)
        if not hasattr(self.state.document, 'feeds'):
            self.state.document.feeds = list()
        self.state.document.feeds.append(text)
        return []


_Copyright = meta_data_directive(copyright, whitespace=True)
directives.register_directive('copyright', _Copyright)

directives.register_directive('time', Time)
directives.register_directive('timezone', Timezone)
directives.register_directive('author', Author)
directives.register_directive('updated', Updated)
directives.register_directive('tag', Tag)
directives.register_directive('feed', Feed)


def publish_parts_doc(source):
    '''A utility function to parse a string into a document and its metadata.
    '''
    args = {'source': source
           ,'source_path': None
           ,'source_class': io.StringInput
           ,'destination_class': io.StringOutput
           ,'destination': None
           ,'destination_path': None
           ,'reader': None, 'reader_name': 'standalone'
           ,'parser': None, 'parser_name': 'restructuredtext'
           ,'writer': None, 'writer_name': 'html'
           ,'settings': None, 'settings_spec': None, 'settings_overrides': None
           ,'config_section': None
           ,'enable_exit_status': None
           }
    output, pub = publish_programmatically(**args)
    return pub.writer.parts, pub.document
