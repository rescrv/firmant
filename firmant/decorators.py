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


'''Decorators used throughout Firmant.
'''


import inspect

import decorator


def in_environment(key):
    '''Assert that `key` is in the environment.

    .. doctest::

       >>> @in_environment('somekey')
       ... def testfunc(environment):
       ...     print 'testfunc executes'
       ...
       >>> inspect.getargspec(testfunc)
       ArgSpec(args=['environment'], varargs=None, keywords=None, defaults=None)
       >>> testfunc({'somekey': True})
       testfunc executes
       >>> testfunc(environment={'somekey': True})
       testfunc executes
       >>> testfunc({})
       Traceback (most recent call last):
       ValueError: Expected 'somekey' in 'environment'

    The decorated function must take a non-keyword attribute for the
    environment.

    .. doctest::

       >>> @in_environment('somekey')
       ... def testfunc():
       ...    print 'testfunc executes'
       ...
       Traceback (most recent call last):
       AttributeError: Decorated function must have arg 'environment'

    Environment cannot have a default value.

    .. doctest::

       >>> @in_environment('somekey')
       ... def testfunc(environment=None):
       ...    print 'testfunc executes'
       ...
       Traceback (most recent call last):
       AttributeError: Decorated function cannot have default value for 'environment'

    '''
    def internal(func):
        '''First internal wrapper.  This is the decorator itself (with key
        bound).
        '''
        _args, _varargs, _varkw, _defaults = inspect.getargspec(func)

        if 'environment' not in _args:
            error = _("Decorated function must have arg 'environment'")
            raise AttributeError(error)

        if _defaults is not None and \
           _args.index('environment') >= len(_args) - len(_defaults):
            error = _("Decorated function cannot have default value " +
                      "for 'environment'")
            raise AttributeError(error)

        def _wrapper_(_func, *args, **kwargs):
            '''The actual wrapped function.

            The signature is updated to match `func`
            '''
            if 'environment' in kwargs:
                environment = kwargs['environment']
            else:
                environment = args[_args.index('environment')]

            if key not in environment:
                error = _("Expected '%s' in 'environment'") % key
                raise ValueError(error)

            return _func(*args, **kwargs)
        return decorator.decorator(_wrapper_, func)
    return internal
