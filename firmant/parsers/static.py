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

from firmant.parsers import Parser
from firmant.du import MetaDataStandaloneReader
from firmant.i18n import _
from firmant.utils import class_name
from firmant.utils.exceptions import log_uncaught_exceptions


__all__ = ['StaticParser']


class StaticObject(object):
    '''An object that serves as a placeholder for a file on the filesystem.
    '''

    __slots__ = ['fullpath', 'relpath', 'permalink']

    def __repr__(self):
        return 'static_obj<%s>' % self.fullpath


class StaticParser(Parser):
    '''Create stand-in objects for static files to be published.

    '''

    def paths(self):
        '''Return a list of paths to objects on the file system.
        '''
        settings = self.settings
        path  = os.path.join(settings.CONTENT_ROOT, settings.STATIC_SUBDIR)
        all_files = []
        for root, dirs, files in os.walk(path):
            for file in files:
                s = StaticObject()
                s.fullpath = os.path.join(root, file)
                if s.fullpath.startswith(path):
                    s.relpath = s.fullpath[len(path):]
                else:
                    raise RuntimeError('Funky paths in StaticParser')
                if s.relpath.startswith('/'):
                    s.relpath = s.relpath[1:]
                all_files.append(s)
        all_files.sort(key=lambda s: s.relpath)
        return all_files

    def parse_one(self, path):
        '''We use the identity function simply because we are copying files.
        '''
        return path
