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


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import firmant.objects


__all__ = ['add_parser', 'add_writer', 'main']


_modules = []
_parsers = []
_writers = []


def add_module(module):
    _modules.append(module)


def add_parser(parser):
    _parsers.append(parser)


def add_writer(writer):
    _writers.append(writer)


def main():
    # Initialize all modules.
    for module in _modules:
        mod()

    # For each parser, parse all objects the parser can handle.
    for parser in _parsers:
        if hasattr(parser, 'parse_all'):
            parser.parse_all()

    # Generate additional objects.
    iterated = set()
    while _parsers and len(iterated) != len(_parsers):
        for parser in _parsers:
            if parser not in iterated and hasattr(parser, 'iterate'):
                if parser.iterate():
                    iterated.add(parser)
            elif parser not in iterated:
                iterated.add(parser)

    # Check for URL conflicts.
    urls = set()

    for key, obj in firmant.objects.retrieve():
        url = firmant.urls.url(key)
        if url and url in urls:
            print('The URL', url, 'is overloaded.')
        if url:
            urls.add(url)

    for writer in _writers:
        if hasattr(writer, 'urls'):
            wurls = writer.urls()
            for url in wurls:
                if url in urls:
                    print('The URL', url, 'is overloaded.')
                urls.add(url)

    # Update objects to use the now exposed URLs
    for key, obj in firmant.objects.retrieve():
        if hasattr(obj, 'update_urls'):
            obj.update_urls()

    # Generate the site.
    for writer in _writers:
        if hasattr(writer, 'write_all'):
            writer.write_all()
