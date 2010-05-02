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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


'''Chunks drive the process of creating a webroot from an input directory.

Each chunk takes as arguments the settings, environment, and publishable
objects and returns a new environment, a new set of objects, and a set of
chunks that should be called in the future.

.. note::

   It must be the case that new chunks are scheduled such that they are called
   after the current chunk.

In this way, the flow of the application may be dynamically modified at the
higher level without placing many strict requirements on what is possible.  The
best practices that should be observed include:

 * A chunk should have a default policy of passing objects unchanged.  Only
   objects that the chunk is intended to modify should be modified by the
   chunks.
 * The same default-unchanged policy should apply to passing the non-object
   environment.
 * New chunks should have a scheduling order such that they are executed after
   the current chunk.

'''


import abc


# pylint: disable-msg=R0903
class AbstractChunk(object):
    '''An :class:`AbstractChunk` defines the interface for all chunks.
    '''

    __metaclass__ = abc.ABCMeta

    def __call__(self, environment, objects):
        '''Execute the chunk with the state from environment/objects.

        The return value should be a tuple `(new_env, new_objs, new_chunks)`.
        The value of `new_env` will replace `environment` in calls to future
        chunks.  The value of `new_objs` will replace `objects` in future
        calls.  New chunks will be added to list of chunks to execute according
        to the scheduling order.

        '''
    # TODO:  Proper decorator syntax http://bugs.python.org/issue8507
    __old_doc__ = __call__.__doc__
    __call__ = abc.abstractmethod(__call__)
    # pylint: disable-msg=W0622
    __call__.__doc__ = __old_doc__
    del __old_doc__

    def scheduling_order(self):
        ''':attr:`scheduling_order` is a positive integer that determines chunk
        execution order.

        :attr:`scheduling_order` uses normal integer comparison.  Chunks of the
        same priority will be executed in arbitrary order.

        '''
    # TODO:  Proper decorator syntax http://bugs.python.org/issue8507
    __old_doc__ = scheduling_order.__doc__
    scheduling_order = abc.abstractproperty(scheduling_order)
    scheduling_order.__doc__ = __old_doc__
    del __old_doc__
