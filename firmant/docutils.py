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

import collections
import os
import os.path
import re
import shlex

import docutils.core
import docutils.io
import docutils.nodes
from docutils.transforms import Transform
from docutils.writers.html4css1 import HTMLTranslator

import firmant.objects
import firmant.urls
from firmant.parser import ParseError


_url_re = re.compile('^`.* <[(](?P<attrs>.*)[)]>`_$')


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

    def __init__(self, key, pub, filters={}, extras={}):
        self._key = key
        self._pub = pub
        self._filters = filters
        self._extras = extras
        self._set_metadata()
        self._set_extras()
        self._set_sections()

    def _set_metadata(self):
        self.title = self._pub.writer.parts['title']
        self.subtitle = self._pub.writer.parts['subtitle']
        names = set()
        for docinfo in self._pub.document.traverse(docutils.nodes.docinfo):
            for elem in docinfo.children:
                if elem.tagname == 'field':
                    name, content = elem.children
                    name, content = name.astext(), content.astext()
                else:
                    name, content = elem.tagname, elem.astext()
                names.add(name)
                if hasattr(self, name):
                    prev = getattr(self, name)
                    if isinstance(prev, collections.MutableSequence):
                        prev.append(content)
                    else:
                        setattr(self, name, [prev, content])
                else:
                    setattr(self, name, content)
        def default(obj):
            if isinstance(obj, collections.MutableSequence):
                return obj[0]
            else:
                return obj
        for name in names:
            setattr(self, name, self._filters.get(name, default)(getattr(self, name)))

    def _set_extras(self):
        for name, func in self._extras.iteritems():
            setattr(self, name, func(self._key, self))

    def _set_sections(self):
        self._sections = [RestSection(x) for x in self._pub.document.traverse(docutils.nodes.section)]

    @property
    def sections(self):
        return self._sections

    def as_html(self):
        return self._pub.writer.parts['fragment']

    def update_urls(self):
        permalink = firmant.urls.url(self._key)
        if permalink:
            self.permalink = permalink
        for reference in self._pub.document.traverse(docutils.nodes.reference):
            match = _url_re.match(reference.rawsource)
            if match:
                attrstr = match.groupdict()['attrs'].encode('ascii')
                attrs = [tuple(x.split('=', 1)) for x in shlex.split(attrstr)]
                attrs = dict(attrs)
                url = firmant.urls.url(attrs)
                if url:
                    reference.set_class('-'.join(['url'] + sorted(attrs.keys())))
                    reference.attributes['refuri'] = url
        for image in self._pub.document.traverse(docutils.nodes.image):
            url = firmant.urls.url({'image': image.get('uri')})
            if url:
                image.attributes['uri'] = url
        self._pub.writer.write(self._pub.document, self._pub.destination)
        self._pub.writer.assemble_parts()


class RestParser(object):

    def __init__(self, fix, regex, metadata, filters={}, extras={}):
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
        self._extras = extras
        if set(fix.keys()) & set(self._regex.groupindex.keys()):
            raise ValueError("Fixed attributes and regex-derived attributes must be disjoint")

    def parse_all(self):
        for root, dirs, files in os.walk('.'):
            for f in files:
                path = os.path.normpath(os.path.join(root, f))
                match = self._regex.match(path)
                if match:
                    key, obj = self.parse(path, match)
                    if key and not firmant.objects.add(key, obj):
                        firmant.parser.report_duplicate_object(path, 'RestParser')

    def parse(self, path, match):
        attrs = match.groupdict()
        attrs.update(self._fix)
        for key, filt in self._filters.iteritems():
            if key in attrs:
                attrs[key] = filt(attrs[key])
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
            rdoc = RestDocument(attrs, pub, self._filters, self._extras)
            for md in self._metadata:
                if not hasattr(rdoc, md):
                    firmant.parser.report_parse_error(path, 'Required metadata field "{0}" is missing'.format(md))
                    return None, None
            return attrs, rdoc
        except docutils.utils.SystemMessage as e:
            msg = e.message
            assert msg.startswith(path)
            lineno, level, msg = msg[len(path):].split(' ', 2)
            lineno = lineno.strip(":")
            msg = msg.strip(".;:")
            firmant.parser.report_parse_error(path, msg + " (on line {0})".format(lineno))
            return None, None
