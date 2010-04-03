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


'''Utilities for manipulating paths/filesystems.
'''


import os
import sys


def cat(path, out=sys.stdout):
    r'''Write the contents of file ``path`` to ``out``.

        >>> m = Mock('output')
        >>> cat('testdata/settings/empty.py', m) #doctest: +ELLIPSIS
        Called output.write('# Copyright (c) 2010, Robert Escriva\n')
        ...
        Called output.write(
            '# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n')

    '''
    f = open(path)
    for line in f:
        print >> out, line,
    f.close()


def create_or_truncate(path):
    r'''Return an ``path`` as an open file, creating dirs if necessary.

    Example::

        >>> import tempfile
        >>> root = tempfile.mkdtemp()
        >>> path = os.path.join(root, 'foo/bar/baz/quux')
        >>> f = create_or_truncate(path)
        >>> f.write('THIS IS THE FIRST TIME\n')
        >>> f.flush() and f.close()

        >>> m = Mock('output')
        >>> cat(path, m)
        Called output.write('THIS IS THE FIRST TIME\n')

        >>> f2 = create_or_truncate(path)
        >>> f2.write('THIS IS THE SECOND TIME\n')
        >>> f2.flush() and f2.close()
        >>> cat(path, m)
        Called output.write('THIS IS THE SECOND TIME\n')

        >>> # Cleanup after ourselves.
        >>> import shutil
        >>> shutil.rmtree(root)

    '''
    par = os.path.dirname(path)
    if par != '':
        try:
            os.makedirs(par)
        except OSError, e:
            if e.errno != 17:
                raise
    return open(path, 'w+')
