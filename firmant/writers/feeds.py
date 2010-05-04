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


'''Abstract base classes for writing feeds.
'''


from firmant import writers


class FeedWriter(writers.Writer):
    '''Write/render individual feed objects.

    This feed writer is serves as the basis for other feed writers (e.g. Atom or
    RSS).

    .. doctest::

       >>> class SampleFeed(FeedWriter):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj):
       ...         print 'Save feed "%s" to "%s"' % (obj.slug, path)
       ...
       >>> sf = SampleFeed({}, {})
       >>> pprint(sf({}, {})) #doctest: +ELLIPSIS
       ({},
        {},
        [<firmant.writers.feeds.SampleFeed object at 0x...>,
         <firmant.writers.feeds.SampleFeed object at 0x...>])

    '''

    def key(self, feed):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a feed object:

            type
               This is always ``feed``.

            slug
               The slug that is unique to the feed object.

        .. doctest::
           :hide:

           >>> class SampleFeed(FeedWriter):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj):
           ...         print 'Save feed "%s" to "%s"' % (obj.slug, path)
           ...
           >>> sf = SampleFeed({}, {'feeds': objects.feeds})

        .. doctest::

           >>> print objects.feeds[0].slug
           foo
           >>> pprint(sf.key(objects.feeds[0]))
           {'slug': u'foo', 'type': u'feed'}

        '''
        return {'type': u'feed', 'slug': feed.slug}

    def obj_list(self, environment, objects):
        '''Return all objects stored under the key ``feeds``.

        .. doctest::
           :hide:

           >>> class SampleFeed(FeedWriter):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj):
           ...         print 'Save feed "%s" to "%s"' % (obj.slug, path)
           ...
           >>> sf = SampleFeed({}, {'feeds': objects.feeds})

        .. doctest::

           >>> sf.obj_list(None, {})
           []
           >>> sf.obj_list(None, {'feeds': []})
           []
           >>> sf.obj_list(None, {'feeds': ['feedobj']})
           ['feedobj']

        '''
        return objects.get('feeds', [])


def _setup(test):
    '''Setup the environment for tests.
    '''
    from testdata.chunks import c900
    test.globs['objects'] = c900
