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

import os
import re

import jinja2

import firmant.objects
import firmant.output
import firmant.urls


_context = {}


class Jinja2TemplateParser(object):

    def __init__(self, fix, regex):
        '''Parse Jinja2 templates.

        All files matching regex will be parsed.  The union of named groups in
        the regex and the fixed attributes will become the set of key-value
        pairs which identify the object.
        '''
        self._fix = fix
        self._regex = re.compile(regex)
        if set(fix.keys()) & set(self._regex.groupindex.keys()):
            raise ValueError("Fixed attributes and regex-derived attributes must be disjoint")

    def parse_all(self):
        for root, dirs, files in os.walk('.'):
            for f in files:
                path = os.path.normpath(os.path.join(root, f))
                match = self._regex.match(path)
                if match:
                    attrs = match.groupdict()
                    attrs.update(self._fix)
                    key, obj = attrs, path
                    if key and not firmant.objects.add(key, obj):
                        firmant.parser.report_duplicate_object(path, 'Jinja2Parser')


class Jinja2TemplateWriter(object):

    def __init__(self, retrieve, context=None, loader=None):
        self._retrieve = retrieve
        self._context = {'url': firmant.urls.url}
        self._context.update(context or {})
        loader = loader or jinja2.PackageLoader('firmant', 'templates')
        self._env = jinja2.Environment(loader=loader)

    def urls(self):
        return set([firmant.urls.url(key) for key, obj in firmant.objects.retrieve(self._retrieve)])

    def write_all(self):
        for key, obj in firmant.objects.retrieve(self._retrieve):
            self.write(key, obj)

    def write(self, key, obj):
        context = _context.copy()
        context.update(self._context)
        template = self._env.get_template(obj)
        data = template.render(context)
        firmant.output.write(key, data)


class Jinja2Writer(object):

    def __init__(self, retrieve, objname, template, context=None, loader=None):
        self._retrieve = retrieve
        self._objname = objname
        self._template = template
        self._context = {'url': firmant.urls.url}
        self._context.update(context or {})
        loader = loader or jinja2.PackageLoader('firmant', 'templates')
        self._env = jinja2.Environment(loader=loader)

    def urls(self):
        return set([firmant.urls.url(key) for key, obj in firmant.objects.retrieve(self._retrieve)])

    def write_all(self):
        for key, obj in firmant.objects.retrieve(self._retrieve):
            self.write(key, obj)

    def write(self, key, obj):
        context = _context.copy()
        context.update(self._context)
        context[self._objname] = obj
        template = self._env.get_template(self._template)
        data = template.render(context)
        firmant.output.write(key, data)


def addglobal(name, obj):
    _context[name] = obj
