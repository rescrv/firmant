# Copyright (c) 2011, Robert Escriva
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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''Almost all behavior of Firmant is controlled via plugins.

The simplest plugin is just a class which inherits from the :class:`Plugin`
class.

.. doctest::

   >>> class SimplestPlugin(Plugin): pass

Plugins may override the load and unload methods, and they will be called at
program start and termination respectively.

.. doctest::

   >>> class LoadUnloadPlugin(Plugin):
   ...     def load(self): pass
   ...     def unload(self): pass
   ...

'''


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement


__all__ = ['Plugin']


class Plugin(object):
    '''The most basic plugin does nothing.

    To create a usable plugin, override the :meth:`load` or :meth:`unload`
    methods.

    .. Make sure that methods which are not overridden work.

    .. doctest::
       :hide:

       >>> p = Plugin()
       >>> p.load()
       >>> p.unload()

    '''

    def __init__(self):
        pass

    def load(self):
        pass

    def unload(self):
        pass