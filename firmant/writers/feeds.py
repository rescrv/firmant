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


'''Base classes for writing feeds.

To use these classes, you only need to pass information specific to your writer.
This typically includes the name of the writer, the extension or file format,
and a rendering function.
'''


from firmant import writers
from firmant.chunks import AbstractChunk


class FeedWriter(AbstractChunk):
    '''Write/render individual feed objects.

    The values of `writername`, `extension` and `render` will be passed directly
    to :class:`firmant.writers.WriterChunk`.  Preconditions specified in
    `preconditions` will be added to the following preconditions:

     * OUTPUT_DIR is specified in the settings.
     * OUTPUT_DIR is an existing directory.
     * OUTPUT_DIR may be written to by the user.
     * There are actually feed objects to write.

    This feed writer is intended to serve as the basis for other feed writers
    (e.g. Atom or RSS).

    .. doctest::

       >>> fw = FeedWriter('SampleWriter', 'txt', [], lambda e, p, o: None)
       >>> fw({}, {}) #doctest: +ELLIPSIS
       ({}, {}, [<firmant.writers.WriterChunk object at 0x...>])

    The :meth:`__key__` method will return a dictionary of attributes that
    identify the object.  `type` and `slug` are the attributes that identify a
    single feed.

    .. doctest::

       >>> print objects.feeds[0].slug
       foo
       >>> pprint(fw.__key__(objects.feeds[0]))
       {'slug': u'foo', 'type': u'feed'}

    The :meth:`__obj_list__` method will return a list of objects that are
    stored in `objects` under the key `feeds`.

    .. doctest::

       >>> fw.__obj_list__(None, {})
       []
       >>> fw.__obj_list__(None, {'feeds': []})
       []
       >>> fw.__obj_list__(None, {'feeds': ['feedobj']})
       ['feedobj']

    '''

    # pylint: disable-msg=R0903

    def __init__(self, writername, extension, preconditions, render):
        super(FeedWriter, self).__init__()
        self.__writername__ = writername
        self.__extension__ = extension
        # TODO:  Actually add the preconditions we said we would.
        self.__preconditions__ = preconditions
        self.__render__ = render

    def __call__(self, environment, objects):
        return (environment, objects,
               [writers.WriterChunk(self.__writername__, self.__extension__,
                   self.__obj_list__, self.__key__, self.__preconditions__,
                   self.__render__)])

    @staticmethod
    def __obj_list__(environment, objects):
        # pylint: disable-msg=W0613
        return objects.get('feeds', [])

    @staticmethod
    def __key__(feed):
        '''Return the set of attributes suitable as input for url mapping.
        '''
        return {'type': u'feed', 'slug': feed.slug}

    scheduling_order = 9


def _setup(test):
    '''Setup the environment for tests.
    '''
    from testdata.chunks import c900
    test.globs['objects'] = c900
