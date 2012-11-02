# Copyright (c) 2012, Robert Escriva
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

import os.path

import crosstex
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from docutils.transforms import Transform

import firmant.docutils

class xtxref(nodes.reference): pass
class xtxlist(nodes.General, nodes.Element): pass

def crosstex_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    cite = xtxref(text, text, format='html')
    cite.xtxkeys = text.split(',')
    return ([cite], [])

roles.register_canonical_role('cite', crosstex_role)

def titlechoices(argument):
    return directives.choice(argument, ('title', 'upper', 'lower'))

class CrossTeXDirective(Directive):
    """ Source code syntax hightlighting.
    """
    required_arguments = 2
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {'titlecase': titlechoices,
                   'add-in': directives.flag,
                   'add-proc': directives.flag,
                   'add-proceedings': directives.flag,
                   'short': directives.unchanged}
    has_content = False

    def run(self):
        xtx = crosstex.CrossTeX(xtx_path=[os.path.join(os.path.join(os.path.expanduser('~'), '.crosstex'))])
        if 'titlecase' in self.options:
            xtx.set_titlecase(self.options['titlecase'])
        if 'add-in' in self.options:
            xtx.add_in()
        if 'add-proc' in self.options:
            xtx.add_proc()
        if 'add-proceedings' in self.options:
            xtx.add_proceedings()
        for s in [f.strip() for f in self.options.get('short', '').split(',') if f]:
            xtx.add_short(s)
        xtxname, style = self.arguments
        xtx.parse(xtxname)
        xtx.set_style('html', style, 'initials')
        x = xtxlist()
        x.xtx = xtx
        x.xtxfile, x.xtxstyle = self.arguments
        return [x]

directives.register_directive('crosstex', CrossTeXDirective)

class CrossTeXCollectTransform(Transform):

    default_priority = 400

    def apply(self):
        if not hasattr(self.document, 'xtxcite'):
            self.document.xtxcite = []
        assert isinstance(self.document.xtxcite, list)
        for node in self.document.traverse(xtxref):
            self.document.xtxcite += node.xtxkeys

class CrossTeXLookupTransform(Transform):

    default_priority = 401

    def apply(self):
        assert isinstance(self.document.xtxcite, list)
        for node in self.document.traverse(xtxlist):
            objects = [(c, node.xtx.lookup(c)) for c in self.document.xtxcite]
            for c in [c for c, o in objects if not o or not o.citeable]:
                raise RuntimeError('Cannot find object for citation %r' % c)
            citeable = [(c, o) for c, o in objects if o and o.citeable]
            citeable = node.xtx.sort(citeable)
            self.document.xtxlabels, rendered = node.xtx.render_with_labels_dict(citeable)
            node.parent.replace(node, nodes.raw('', rendered, format='html'))

class CrossTeXLabelTransform(Transform):

    default_priority = 402

    def apply(self):
        assert isinstance(self.document.xtxcite, list)
        for node in self.document.traverse(xtxref):
            if not hasattr(self.document, 'xtxlabels'):
                raise RuntimeError('Citations without CrossTeX block')
            assert isinstance(self.document.xtxlabels, dict)
            labels = self.document.xtxlabels
            label = '['
            cites = []
            for k in node.xtxkeys:
                cites.append('<a href="#xtx:%s">%s</a>' % (labels[k], labels[k]))
            label += ', '.join(cites)
            label += ']'
            node.parent.replace(node, nodes.raw('', label, format='html'))

firmant.docutils.add_transform(CrossTeXCollectTransform)
firmant.docutils.add_transform(CrossTeXLookupTransform)
firmant.docutils.add_transform(CrossTeXLabelTransform)
