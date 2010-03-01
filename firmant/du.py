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

from firmant.utils import strptime


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


def time(d, content):
    '''Interpret the content as a time.

    Using just hours::

        >>> d = dict()
        >>> time(d, ['15'])
        >>> d['time']
        datetime.time(15, 0)

    Using hours and minutes::

        >>> d = dict()
        >>> time(d, ['15:43'])
        >>> d['time']
        datetime.time(15, 43)

    Using hours, minutes, and seconds::

        >>> d = dict()
        >>> time(d, ['15:43:42'])
        >>> d['time']
        datetime.time(15, 43, 42)

    ValueError is raised on invalid time::

        >>> d = dict()
        >>> time(d, ['154342'])
        Traceback (most recent call last):
        ValueError: time data '154342' does not match any format.

    '''
    formats = ['%H', '%H:%M', '%H:%M:%S']
    dt = strptime(''.join(content), formats)
    d['time'] = dt.time()


def single_line(d, content, attr='line'):
    '''Interpret the content as a single line.

    Default behavior::

        >>> d = dict()
        >>> single_line(d, [u'foobar'])
        >>> d['line']
        u'foobar'

    Specifying the attribute to save to::

        >>> d = dict()
        >>> single_line(d, [u'foobar'], 'attr')
        >>> d['attr']
        u'foobar'

    '''
    d[attr] = ''.join(content)


def updated(d, content):
    '''Interpret content as a full datetime.

    YYYY-MM-DD HH:MM:SS (time may be omitted)::

        >>> d = dict()
        >>> updated(d, ['2009-02-01 14:15:51'])
        >>> d['updated']
        datetime.datetime(2009, 2, 1, 14, 15, 51)

    MM-DD-YYYY HH:MM:SS (time may be omitted)::

        >>> d = dict()
        >>> updated(d, ['02-01-2009 14:15:51'])
        >>> d['updated']
        datetime.datetime(2009, 2, 1, 14, 15, 51)

    ValueError is raised on invalid datetime::

        >>> d = dict()
        >>> updated(d, ['154342'])
        Traceback (most recent call last):
        ValueError: time data '154342' does not match any format.

    '''
    formats = ['%Y-%m-%d', '%Y-%m-%d %H', '%Y-%m-%d %H:%M',
               '%Y-%m-%d %H:%M:%S', '%m-%d-%Y', '%m-%d-%Y %H',
               '%m-%d-%Y %H:%M', '%m-%d-%Y %H:%M:%S']
    d['updated'] = strptime(''.join(content), formats)


def list_element(d, content, attr='element_plural'):
    '''Interpret content as an element in a list.

    MetaData of this type may have several directives, each of which appends a
    value to list.

    It returns a list so that the metadata transforms may simply append tags::

        >>> d = dict()
        >>> list_element(d, [u'foo'])
        >>> d['element_plural']
        [u'foo']

    An attribute for storing values may be provided::

        >>> d = dict()
        >>> list_element(d, [u'foo'], 'attr')
        >>> d['attr']
        [u'foo']

    '''
    d[attr] = list([''.join(content)])


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

_Time = meta_data_directive(time)
directives.register_directive('time', _Time)

_Timezone = meta_data_directive(lambda d, c: single_line(d, c, 'timezone'))
directives.register_directive('timezone', _Timezone)

_Author = meta_data_directive(lambda d, c: single_line(d, c, 'author'))
directives.register_directive('author', _Author)

_Updated = meta_data_directive(updated)
directives.register_directive('updated', _Updated)

_Tag = meta_data_directive(lambda d, c: list_element(d, c, 'tags'))
directives.register_directive('tag', _Tag)

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
