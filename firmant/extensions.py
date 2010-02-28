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


'''Base classes and functions for creating extension mount points.

Actual extensions are not within the extensions module.
'''


from copy import copy


__all__ = ['ExtensionManager']


class ExtensionManager(object):
    '''Setup and store all registered extensions.

    Each registered extension (be it a module, class, or instance) is expected
    to have a callable ``setup()`` that is suitable for calling with no
    arguments.

    Basic usage::

        >>> class DummyExt(object):
        ...     def __init__(self, name):
        ...         self._name = name
        ...     def setup(self):
        ...         print 'Initializing %s' % self._name
        ...     def __repr__(self):
        ...         return '<Instance of DummyExt %s>' % self._name
        >>>
        >>> em = ExtensionManager()
        >>> em.list()
        []
        >>> foo = DummyExt('foo')
        >>> bar = DummyExt('bar')
        >>> em.register(foo)
        Initializing foo
        >>> em.register(bar)
        Initializing bar
        >>> em.list()
        [<Instance of DummyExt foo>, <Instance of DummyExt bar>]
        >>> em.remove(foo)
        >>> em.list()
        [<Instance of DummyExt bar>]

    Exception cases::

        >>> em.remove(foo)
        Traceback (most recent call last):
        RuntimeError: Extension "<Instance of DummyExt foo>" not registered.

        >>> em.register(bar)
        Traceback (most recent call last):
        RuntimeError: Extension "<Instance of DummyExt bar>" already registered.

        >>> em.register(object()) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        RuntimeError: Extension "<object object at 0x...>" has no ``setup``.

        >>> class NoncallableSetup(object):
        ...     setup = 'HI'
        >>> em.register(NoncallableSetup) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        RuntimeError: Extension "<...>"'s ``setup`` is not callable.

    '''

    def __init__(self):
        self._list = list()

    def list(self):
        return copy(self._list)

    def register(self, ext):
        if ext in self._list:
            raise RuntimeError('Extension "%s" already registered.' % repr(ext))
        if not hasattr(ext, 'setup'):
            raise RuntimeError('Extension "%s" has no ``setup``.' % repr(ext))
        if not callable(ext.setup):
            error = '''Extension "%s"'s ``setup`` is not callable.'''
            raise RuntimeError(error % repr(ext))
        ext.setup()
        self._list.append(ext)

    def remove(self, ext):
        if ext not in self._list:
            raise RuntimeError('Extension "%s" not registered.' % repr(ext))
        self._list = filter(lambda e: e != ext, self._list)
