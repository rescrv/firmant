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


from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.core import publish_programmatically
from docutils import io


class Copyright(Directive):
    '''A restructured text directive for copyright information.
    '''

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    has_content = True

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        text = '\n'.join(self.content)
        self.state.document.copyright = text
        return []


directives.register_directive('copyright', Copyright)


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
