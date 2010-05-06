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


from firmant import paginate
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


class PostArchiveAll(writers.Writer):
    '''Write the posts into paginated pages.

    .. doctest::

       >>> class SamplePostArchiveAll(PostArchiveAll):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj): pass
       >>> spaa = SamplePostArchiveAll({}, {})

    '''

    def key(self, obj):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a archived year page:

            type
               This is always ``post``.

            page
               The 1-indexed page number of the page.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveAll(PostArchiveAll):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spaa = SamplePostArchiveAll({}, {})

        .. doctest::

           >>> obj = spaa.obj_list({'settings': settings},
           ...                     {'posts': objects.posts})[0]
           >>> pprint(obj) #doctest: +ELLIPSIS
           ([<firmant.parsers.RstObject object at 0x...>,
             <firmant.parsers.RstObject object at 0x...>],
            Paginated(None, 1, 2))

           >>> pprint(spaa.key(obj))
           {'page': 1, 'type': u'post'}

        '''
        return {'type': u'post'
               ,'page': obj[1].cur
               }

    def obj_list(self, environment, objects):
        '''Return 3-tuples with the list of objects and prev/next information.

        The prev/next information is stored in
        :class:`firmant.paginate.Paginated` objects and is returned for both the
        groupings by year, and for the groupings into pages.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveAll(PostArchiveAll):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spaa = SamplePostArchiveAll({}, {})

        .. doctest::

           >>> spaa.obj_list({'settings': settings}, {})
           []
           >>> spaa.obj_list({'settings': settings}, {'posts': []})
           []
           >>> pprint(spaa.obj_list({'settings': settings},
           ...                      {'posts': objects.posts})) #doctest: +ELLIPSIS
           [([<firmant.parsers.RstObject object at 0x...>,
              <firmant.parsers.RstObject object at 0x...>],
             Paginated(None, 1, 2)),
            ([<firmant.parsers.RstObject object at 0x...>,
              <firmant.parsers.RstObject object at 0x...>],
             Paginated(1, 2, 3)),
            ([<firmant.parsers.RstObject object at 0x...>], Paginated(2, 3, None))]

        '''
        num_per_page = environment['settings'].POSTS_PER_PAGE
        posts = [p for p in reversed(sorted(objects.get('posts', []),
                       key=lambda p: (p.published, p.slug)))]
        return paginate.paginate(num_per_page, posts)


class PostArchiveYearly(writers.Writer):
    '''Write the posts into pages grouped by year and then paginated.

    .. doctest::

       >>> class SamplePostArchiveYearly(PostArchiveYearly):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj): pass
       >>> spay = SamplePostArchiveYearly({}, {})

    '''

    def key(self, obj):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a archived year page:

            type
               This is always ``post``.

            year
               The year of publication.

            page
               The 1-indexed page number of the page.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveYearly(PostArchiveYearly):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spay = SamplePostArchiveYearly({}, {})

        .. doctest::

           >>> obj = spay.obj_list({'settings': settings},
           ...                     {'posts': objects.posts})[0]
           >>> pprint(obj) #doctest: +ELLIPSIS
           ([<firmant.parsers.RstObject object at 0x...>],
            Paginated(None, (2010,), (2009,)),
            Paginated(None, 1, 2))
           >>> pprint(spay.key(obj))
           {'page': 1, 'type': u'post', 'year': 2010}

        '''
        return {'type': u'post'
               ,'year': obj[1].cur[0]
               ,'page': obj[2].cur
               }

    def obj_list(self, environment, objects):
        '''Return 3-tuples with the list of objects and prev/next information.

        The prev/next information is stored in
        :class:`firmant.paginate.Paginated` objects and is returned for both the
        groupings by year, and for the groupings into pages.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveYearly(PostArchiveYearly):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spay = SamplePostArchiveYearly({}, {})

        .. doctest::

           >>> spay.obj_list({'settings': settings}, {})
           []
           >>> spay.obj_list({'settings': settings}, {'posts': []})
           []
           >>> pprint(spay.obj_list({'settings': settings},
           ...                      {'posts': objects.posts})) #doctest: +ELLIPSIS
           [([<firmant.parsers.RstObject object at 0x...>,
              <firmant.parsers.RstObject object at 0x...>],
             Paginated(None, (2010,), (2009,)),
             Paginated(None, 1, 2)),
            ([<firmant.parsers.RstObject object at 0x...>,
              <firmant.parsers.RstObject object at 0x...>],
             Paginated(None, (2010,), (2009,)),
             Paginated(1, 2, None)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated((2010,), (2009,), None),
             Paginated(None, 1, None))]

        '''
        num_per_page = environment['settings'].POSTS_PER_PAGE
        posts = [p for p in reversed(sorted(objects.get('posts', []),
                       key=lambda p: (p.published, p.slug)))]
        return paginate.split_paginate(num_per_page, self.__splitfunc__, posts)

    @staticmethod
    def __splitfunc__(post):
        return (post.published.year,)


class PostArchiveMonthly(writers.Writer):
    '''Write the posts into pages grouped by month and then paginated.

    .. doctest::

       >>> class SamplePostArchiveMonthly(PostArchiveMonthly):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj): pass
       >>> spam = SamplePostArchiveMonthly({}, {})

    '''

    def key(self, obj):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify a archived month page:

            type
               This is always ``post``.

            year
               The year of publication.

            month
               The month of publication.

            page
               The 1-indexed page number of the page.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveMonthly(PostArchiveMonthly):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spam = SamplePostArchiveMonthly({}, {})

        .. doctest::

           >>> obj = spam.obj_list({'settings': settings},
           ...                     {'posts': objects.posts})[0]
           >>> pprint(obj) #doctest: +ELLIPSIS
           ([<firmant.parsers.RstObject object at 0x...>,
             <firmant.parsers.RstObject object at 0x...>],
            Paginated(None, (2010, 2), (2010, 1)),
            Paginated(None, 1, 2))
           >>> pprint(spam.key(obj))
           {'month': 2, 'page': 1, 'type': u'post', 'year': 2010}

        '''
        return {'type': u'post'
               ,'year': obj[1].cur[0]
               ,'month': obj[1].cur[1]
               ,'page': obj[2].cur
               }

    def obj_list(self, environment, objects):
        '''Return 3-tuples with the list of objects and prev/next information.

        The prev/next information is stored in
        :class:`firmant.paginate.Paginated` objects and is returned for both the
        groupings by month, and for the groupings into pages.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveMonthly(PostArchiveMonthly):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spam = SamplePostArchiveMonthly({}, {})

        .. doctest::

           >>> spam.obj_list({'settings': settings}, {})
           []
           >>> spam.obj_list({'settings': settings}, {'posts': []})
           []
           >>> pprint(spam.obj_list({'settings': settings},
           ...                      {'posts': objects.posts})) #doctest: +ELLIPSIS
           [([<firmant.parsers.RstObject object at 0x...>,
              <firmant.parsers.RstObject object at 0x...>],
             Paginated(None, (2010, 2), (2010, 1)),
             Paginated(None, 1, 2)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated(None, (2010, 2), (2010, 1)),
             Paginated(1, 2, None)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated((2010, 2), (2010, 1), (2009, 12)),
             Paginated(None, 1, None)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated((2010, 1), (2009, 12), None),
             Paginated(None, 1, None))]

        '''
        num_per_page = environment['settings'].POSTS_PER_PAGE
        posts = [p for p in reversed(sorted(objects.get('posts', []),
                       key=lambda p: (p.published, p.slug)))]
        return paginate.split_paginate(num_per_page, self.__splitfunc__, posts)

    @staticmethod
    def __splitfunc__(post):
        return (post.published.year, post.published.month)


class PostArchiveDaily(writers.Writer):
    '''Write the posts into pages grouped by day and then paginated.

    .. doctest::

       >>> class SamplePostArchiveDaily(PostArchiveDaily):
       ...     extension = 'txt'
       ...     def render(self, environment, path, obj): pass
       >>> spad = SamplePostArchiveDaily({}, {})

    '''

    def key(self, obj):
        '''Return the set of attributes suitable as input for url mapping.

        Attributes that identify an archived day page:

            type
               This is always ``post``.

            year
               The year of publication.

            month
               The month of publication.

            day
               The day of publication.

            page
               The 1-indexed page number of the page.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveDaily(PostArchiveDaily):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spad = SamplePostArchiveDaily({}, {})

        .. doctest::

           >>> obj = spad.obj_list({'settings': settings},
           ...                     {'posts': objects.posts})[0]
           >>> pprint(obj) #doctest: +ELLIPSIS
           ([<firmant.parsers.RstObject object at 0x...>,
             <firmant.parsers.RstObject object at 0x...>],
            Paginated(None, (2010, 2, 2), (2010, 2, 1)),
            Paginated(None, 1, None))
           >>> pprint(spad.key(obj))
           {'day': 2, 'month': 2, 'page': 1, 'type': u'post', 'year': 2010}

        '''
        return {'type': u'post'
               ,'year': obj[1].cur[0]
               ,'month': obj[1].cur[1]
               ,'day': obj[1].cur[2]
               ,'page': obj[2].cur
               }

    def obj_list(self, environment, objects):
        '''Return 3-tuples with the list of objects and prev/next information.

        The prev/next information is stored in
        :class:`firmant.paginate.Paginated` objects and is returned for both the
        groupings by day, and for the groupings into pages.

        .. doctest::
           :hide:

           >>> class SamplePostArchiveDaily(PostArchiveDaily):
           ...     extension = 'txt'
           ...     def render(self, environment, path, obj): pass
           >>> spad = SamplePostArchiveDaily({}, {})

        .. doctest::

           >>> spad.obj_list({'settings': settings}, {})
           []
           >>> spad.obj_list({'settings': settings}, {'posts': []})
           []
           >>> pprint(spad.obj_list({'settings': settings},
           ...                      {'posts': objects.posts})) #doctest: +ELLIPSIS
           [([<firmant.parsers.RstObject object at 0x...>,
              <firmant.parsers.RstObject object at 0x...>],
             Paginated(None, (2010, 2, 2), (2010, 2, 1)),
             Paginated(None, 1, None)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated((2010, 2, 2), (2010, 2, 1), (2010, 1, 1)),
             Paginated(None, 1, None)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated((2010, 2, 1), (2010, 1, 1), (2009, 12, 31)),
             Paginated(None, 1, None)),
            ([<firmant.parsers.RstObject object at 0x...>],
             Paginated((2010, 1, 1), (2009, 12, 31), None),
             Paginated(None, 1, None))]

        '''
        num_per_page = environment['settings'].POSTS_PER_PAGE
        posts = [p for p in reversed(sorted(objects.get('posts', []),
                       key=lambda p: (p.published, p.slug)))]
        return paginate.split_paginate(num_per_page, self.__splitfunc__, posts)

    @staticmethod
    def __splitfunc__(post):
        return (post.published.year, post.published.month, post.published.day)


def _setup(test):
    '''Setup the environment for tests.
    '''
    from pysettings.settings import Settings
    from testdata.chunks import c900
    settings = Settings()
    settings.POSTS_PER_PAGE = 2
    test.globs['settings'] = settings
    test.globs['objects'] = c900
