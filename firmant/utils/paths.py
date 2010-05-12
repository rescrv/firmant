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
import re
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


def recursive_listdir(root, matches=None, files_only=True):
    '''Provide a list of all files in a directory and its subdirectories.

    .. doctest::

       >>> pprint(sorted(recursive_listdir('testdata/pristine/posts')))
       ['2009-12-31-party.rst',
        '2010-01-01-newyear.rst',
        '2010-02-01-newmonth.rst',
        '2010-02-02-newday.rst',
        '2010-02-02-newday2.rst']

    An optional regex string `matches` may be specified and will be compared to
    the :func:`os.path.basename` of each entry under path.

    .. doctest::

       >>> pprint(sorted(recursive_listdir('testdata/pristine',
       ...                                 matches='.*\.rst$')))
       ['feeds/bar.rst',
        'feeds/baz.rst',
        'feeds/foo.rst',
        'feeds/quux.rst',
        'flat/about.rst',
        'flat/empty.rst',
        'flat/links.rst',
        'posts/2009-12-31-party.rst',
        'posts/2010-01-01-newyear.rst',
        'posts/2010-02-01-newmonth.rst',
        'posts/2010-02-02-newday.rst',
        'posts/2010-02-02-newday2.rst',
        'tags/bar.rst',
        'tags/baz.rst',
        'tags/foo.rst',
        'tags/quux.rst']

    '''
    ret = []
    for relroot, dirs, files in os.walk(root):
        if files_only:
            dirs = []
        for ent in dirs + files:
            path = os.path.join(relroot, ent)
            if path.startswith(root):
                path = path[len(root):]
            else:
                raise RuntimeError(_('`path` expected to exist under `root`'))
            if path.startswith('/'):
                path = path[1:]
            if not matches or re.match(matches, path):
                ret.append(path)
    return ret
