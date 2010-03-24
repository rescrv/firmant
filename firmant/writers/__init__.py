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


'''Writers create the filesystem to be published.

Each writer will handle a subset of the objs, and create a portion of the
outputted directory hierarchy.
'''


import abc
import collections
import logging

from firmant.i18n import _
from firmant.utils import class_name


class Writer(object):
    '''Handle writing parsed objects to the filesystem.

    It is assumed that a writer will have the following methods::

        - write:  Write all objects to the filesystem.
        - write_preconditions:  Tests that the writer is able to write.  If this
          returns False, it is likely that the writer would fail.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, settings, objs, urlmapper):
        self.settings = settings
        self.objs = objs
        self.urlmapper = urlmapper
        self.log = logging.getLogger(class_name(self.__class__))

    @abc.abstractmethod
    def urls(self):
        '''A list of paths that the writer will write.

        Each path is assumed to be relative to the webroot of the blog.  It is
        implicit that paths begin with '/' (e.g. the path 'foo/bar' translates
        implies a request URI of '/foo/bar').
        '''

    @abc.abstractmethod
    def write(self):
        '''Write the objects to the filesystem.
        '''

    def write_preconditions(self):
        '''Returns true if and only if it is acceptable to proceed with writing.
        '''
        # Fail if we do not have an output directory.
        if getattr(self.settings, 'OUTPUT_DIR', None) is None:
            self.log.critical(_('``OUTPUT_DIR`` not defined in settings.'))
            return False
        return True
