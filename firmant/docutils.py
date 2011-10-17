# Copyright (c) 2011, Robert Escriva
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


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import re

import docutils.core
import docutils.io
import docutils.nodes
from docutils.writers.html4css1 import HTMLTranslator

from firmant.parser import ParseError


class RestSection(object):

    def __init__(self, node):
        self._node = node

    @property
    def id(self):
        return self._node.get('ids')[0]

    def as_html(self):
        visitor = HTMLTranslator(self._node.document)
        self._node.walkabout(visitor)
        return ''.join(visitor.body)


class RestDocument(object):
    '''A fully parsed reStructuredText document.
    '''

    def __init__(self, pub, filters={}):
        self._pub = pub
        self._filters = filters
        self._set_metadata()
        self._set_sections()

    def _set_metadata(self):
        for docinfo in self._pub.document.traverse(docutils.nodes.docinfo):
            for elem in docinfo.children:
                if elem.tagname == 'field':
                    name, content = elem.children
                    name, content = name.astext(), content.astext()
                else:
                    name, content = elem.tagname, elem.astext()
                content = self._filters.get(name, lambda x: x)(content)
                setattr(self, name, content)
        self.title = self._pub.writer.parts['title']
        self.subtitle = self._pub.writer.parts['subtitle']

    def _set_sections(self):
        self._sections = [RestSection(x) for x in self._pub.document.traverse(docutils.nodes.section)]

    @property
    def sections(self):
        return self._sections

    def as_html(self):
        return self._pub.writer.parts['html_body']


class RestParser(object):

    def __init__(self, fix, regex, metadata, filters={}):
        '''Parse RestDocuments.

        All files matching regex will be parsed.  The union of named groups in
        the regex and the fixed attributes will become the set of key-value
        pairs which identify the parsed document.

        Each parsed document will be checked to see that it includes the
        specified metadata.
        '''
        self._fix = fix
        self._metadata = metadata
        self._regex = re.compile(regex)
        self._filters = filters
        if set(fix.keys()) & set(self._regex.groupindex.keys()):
            raise ValueError("Fixed attributes and regex-derived attributes must be disjoint")

    def matches(self, path):
        return self._regex.match(path) is not None

    def parse(self, path):
        attrs = self._regex.match(path).groupdict()
        attrs.update(self._fix)
        settings_overrides = {'initial_header_level': '2'
                             ,'warning_stream': False
                             ,'report_level': 6
                             ,'halt_level': 2
                             }
        pub = docutils.core.Publisher(destination_class=docutils.io.StringOutput)
        pub.set_components('standalone', 'restructuredtext', 'html')
        pub.process_programmatic_settings(None, settings_overrides, None)
        pub.set_source(source_path=path)
        try:
            pub.publish()
            rdoc = RestDocument(pub, self._filters)
            for md in self._metadata:
                if not hasattr(rdoc, md):
                    raise ParseError('Required metadata field "{0}" is missing'.format(md))
            return attrs, rdoc
        except docutils.utils.SystemMessage as e:
            msg = e.message
            assert msg.startswith(path)
            lineno, level, msg = msg[len(path):].split(' ', 2)
            lineno = lineno.strip(":")
            msg = msg.strip(".;:")
            raise ParseError(msg + " (on line {0}).".format(lineno))
