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


def log_uncaught_exceptions(func, log, message, save_traceback=False):
    '''Catch and log exceptions of ``func``.

    Returns True if the function succeeds without throwing an exception.

    `message` will be written to `log` if an exception is thrown, and False is
    returned.  If save_trackback is true, the traceback will be saved to a
    temporary file.

    In the normal case, the `func` will be called and True will be returned.

    .. doctest::
       :hide:

       >>> log = Mock('log')

    .. doctest::

       >>> def wont_raise_error():
       ...     print 'Success!'
       >>> log_uncaught_exceptions(wont_raise_error, log, 'error!')
       Success!
       True

    When `func` raises an error, the error will be caught, and `message` will be
    written to log as an error.

    .. doctest::

       >>> def raises_error():
       ...     raise RuntimeError('Intentionally thrown')
       >>> log_uncaught_exceptions(raises_error, log, 'error!')
       Called log.error('error!')
       Called log.info('traceback not saved')
       False

    If `save_traceback` is True, then a temporary file created with
    `tempfile.mkstemp` will be used to store the traceback.

    .. doctest::
       :hide:

       >>> import tempfile
       >>> f, path = tempfile.mkstemp()
       >>> tempfile.mkstemp = Mock('mkstemp')
       >>> tempfile.mkstemp.mock_returns = (f, path)

    .. doctest::

       >>> log_uncaught_exceptions(raises_error, log, 'error!', True) #doctest: +ELLIPSIS
       Called log.error('error!')
       Called mkstemp(prefix='firmant', text=True)
       Called log.error('...traceback saved to /...')
       False

    .. doctest::
       :hide:

       >>> os.unlink(path)
       >>> from minimock import restore
       >>> restore()

    If an exception is thrown while saving to the file, it will warn about
    the potential for infinite recursion and stop:

    .. doctest::
       :hide:

       >>> tempfile.mkstemp = Mock('mkstemp')
       >>> tempfile.mkstemp.mock_raises = ValueError

    .. doctest::

       >>> log_uncaught_exceptions(raises_error, log, 'error!', True)
       Called log.error('error!')
       Called mkstemp(prefix='firmant', text=True)
       Called log.error("it's turtles all the way down")
       False

    .. doctest::
       :hide:

       >>> from minimock import restore
       >>> restore()

    '''
    try:
        func()
    # pylint: disable-msg=W0702
    except:
        log.error(message)
        if save_traceback:
            try:
                tmp, path = tempfile.mkstemp(prefix='firmant', text=True)
                tmp = os.fdopen(tmp, 'w+')
                traceback.print_exc(file=tmp)
                tmp.flush()
                tmp.close()
                log.error(_('traceback saved to %s') % path)
            except:
                log.error(_("it's turtles all the way down"))
        else:
            log.info(_('traceback not saved'))
    else:
        return True
    return False
