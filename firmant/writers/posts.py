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


'''Abstract base classes for writing posts.
'''


from firmant import writers


class PostWriter(writers.Writer):
    '''Write/render individual post objects.

    This post writer is serves as the basis for other post writers that write
    posts individually.

    .. doctest::

       >>> class SamplePost(PostWriter):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj):
       ...         print 'Save post "%s %s" to "%s"' % \
                       (obj.published.strftime('%Y-%m-%d'), obj.slug, path)
       >>> sp = SamplePost({}, {})
       >>> pprint(sp({}, {})) #doctest: +ELLIPSIS
       ({},
        {},
        [<firmant.writers.posts.SamplePost object at 0x...>,
         <firmant.writers.posts.SamplePost object at 0x...>])

    '''

    def key(self, post):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a post object:

            type
               This is always ``post``.

            year
               The year of publication.

            month
               The month of publication.

            day
               The day of publication.

            slug
               The slug that is unique to the feed object.

        .. doctest::
           :hide:

           >>> class SamplePost(PostWriter):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj):
           ...         print 'Save post "%s %s" to "%s"' % \
                           (obj.published.strftime('%Y-%m-%d'), obj.slug, path)
           >>> sp = SamplePost({}, {})

        .. doctest::

           >>> print objects.posts[0].published.date(), objects.posts[0].slug
           2009-12-31 party
           >>> pprint(sp.key(objects.posts[0]))
           {'day': 31, 'month': 12, 'slug': u'party', 'type': u'post', 'year': 2009}

        '''
        return {'type': u'post'
               ,'slug': post.slug
               ,'year': post.published.year
               ,'month': post.published.month
               ,'day': post.published.day
               }

    def obj_list(self, environment, objects):
        '''Return all objects stored under the key ``posts``.

        .. doctest::
           :hide:

           >>> class SamplePost(PostWriter):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj):
           ...         print 'Save post "%s %s" to "%s"' % \
                           (obj.published.strftime('%Y-%m-%d'), obj.slug, path)
           >>> sp = SamplePost({}, {})

        .. doctest::

           >>> sp.obj_list(None, {})
           []
           >>> sp.obj_list(None, {'posts': []})
           []
           >>> sp.obj_list(None, {'posts': ['postobj']})
           ['postobj']

        '''
        return objects.get('posts', [])


def _setup(test):
    '''Setup the environment for tests.
    '''
    from testdata.chunks import c900
    test.globs['objects'] = c900
