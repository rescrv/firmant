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


def cat(path, out=None):
    r'''Write the contents of file ``path`` to ``out``.

    .. doctest::
       :hide:

       >>> import sys

    .. doctest::

       >>> cat('testdata/settings/empty.py') #doctest: +ELLIPSIS
       # Copyright (c) 2010, Robert Escriva
       ...
       # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    '''
    fil = open(path)
    if out is None:
        out = sys.stdout
    for line in fil:
        print >> out, line,
    fil.close()


def create_or_truncate(path):
    r'''Open ``path``, creating it or directories as necessary.

    In this example, the file `path` is `foo/bar/baz/quux` relative to a
    temporary directory.  It is opened once for reading and the string ``THIS IS
    THE FIRST TIME`` is written to the file.  The file is closed and reopened
    using create_or_truncate, and written again with ``THIS IS THE SECOND
    TIME``.

    .. doctest::
       :hide:

       >>> import tempfile
       >>> root = tempfile.mkdtemp()

    .. doctest::

       >>> path = os.path.join(root, 'foo/bar/baz/quux')

       >>> f = create_or_truncate(path)
       >>> f.write('THIS IS THE FIRST TIME\n')
       >>> f.flush() and f.close()

       >>> cat(path)
       THIS IS THE FIRST TIME

       >>> f2 = create_or_truncate(path)
       >>> f2.write('THIS IS THE SECOND TIME\n')
       >>> f2.flush() and f2.close()

       >>> cat(path)
       THIS IS THE SECOND TIME

    .. doctest::
       :hide:

       >>> # Cleanup after ourselves.
       >>> import shutil
       >>> shutil.rmtree(root)

    Errors from the underlying operating system will be raised.

    .. doctest::

       >>> create_or_truncate('/tmp')
       Traceback (most recent call last):
       IOError: [Errno 21] Is a directory: '/tmp'

    .. doctest::
       :hide:

       >>> from minimock import restore
       >>> old_makedirs = os.makedirs
       >>> os.makedirs = Mock('makedirs')
       >>> os.makedirs.mock_raises = OSError(21)
       >>> os.makedirs.mock_raises.errno = 21
       >>> create_or_truncate('/')
       Traceback (most recent call last):
       OSError: 21
       >>> os.makedirs = old_makedirs

    '''
    par = os.path.dirname(path)
    if par != '':
        try:
            os.makedirs(par)
        except OSError, ex:
            if ex.errno != 17:
                raise
    return open(path, 'w+')
