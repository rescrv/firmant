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


'''Utilities for handling or silencing exceptions.
'''


import os
import tempfile
import traceback

from firmant.i18n import _


def log_uncaught_exceptions(func, log, message, save_traceback=False):
    '''Catch and log exceptions of ``func``.

    Returns True if the function succeeded without throwing an exception.

    A function for safely calling code that may throw exceptions and logging any
    exceptions thrown.  Optionally it will save the traceback to a file::

        >>> def raises_error():
        ...     raise RuntimeError('Intentionally thrown')
        >>> log_uncaught_exceptions(raises_error, Mock('log'), 'error!')
        Called log.error('error!')
        Called log.info('traceback not saved')
        False

    If ``save_traceback`` is True, it will save the file to one created with
    ``tempfile.mkstemp``.

        >>> from minimock import restore
        >>> import tempfile
        >>> f, path = tempfile.mkstemp()
        >>> tempfile.mkstemp = Mock('mkstemp')
        >>> tempfile.mkstemp.mock_returns = (f, path)
        >>> def raises_error():
        ...     raise RuntimeError('Intentionally thrown')
        >>> log_uncaught_exceptions(raises_error, Mock('log'), 'error!', True) #doctest: +ELLIPSIS
        Called log.error('error!')
        Called mkstemp(prefix='firmant', text=True)
        Called log.error(...'traceback saved to /...')
        False
        >>> os.unlink(path)
        >>> restore()

    If an exception is thrown while saving to the file, it will warn about
    the potential for infinite recursion and stop::

        >>> from minimock import restore
        >>> import tempfile
        >>> tempfile.mkstemp = Mock('mkstemp')
        >>> tempfile.mkstemp.mock_raises = ValueError
        >>> def raises_error():
        ...     raise RuntimeError('Intentionally thrown')
        >>> log_uncaught_exceptions(raises_error, Mock('log'), 'error!', True)
        Called log.error('error!')
        Called mkstemp(prefix='firmant', text=True)
        Called log.error("it's turtles all the way down")
        False
        >>> restore()

    '''
    try:
        func()
    except:
        log.error(message)
        if save_traceback:
            try:
                t, path = tempfile.mkstemp(prefix='firmant', text=True)
                t = os.fdopen(t, 'w+')
                traceback.print_exc(file=t)
                t.flush()
                t.close()
                log.error(_('traceback saved to %s') % path)
            except:
                import sys
                log.error(_("it's turtles all the way down"))
        else:
            log.info(_('traceback not saved'))
    else:
        return True
    return False
