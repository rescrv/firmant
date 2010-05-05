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


'''Paginate or group objects according to certain properties.
'''


class Paginated(object):
    '''An object representing keys in paginated lists.

    The key used for each of the lists is stored in the properties ``prev``,
    ``cur``, ``next``.  Instances are just nice containers in place of
    3-tuples::

    .. doctest::

       >>> p = Paginated(1, 2, 3)
       >>> p
       Paginated(1, 2, 3)
       >>> p.prev
       1
       >>> p.cur
       2
       >>> p.next
       3

    '''

    def __init__(self, prev, cur, nex):
        self._prev = prev
        self._cur = cur
        self._next = nex

    @property
    def prev(self):
        '''The key of the previous list.
        '''
        return self._prev

    @property
    def cur(self):
        '''The key of the current list.
        '''
        return self._cur

    @property
    def next(self):
        '''The key of the next list.
        '''
        return self._next

    def __repr__(self):
        '''A more human-friendly form for representing paginated objects.
        '''
        return 'Paginated(%s, %s, %s)' % \
               (str(self._prev), str(self._cur), str(self._next))


def split_list(key_func, obj_list):
    '''Split `obj_list` at boundaries determined by key_func.

    At each point the return value of `key_func(obj)` changes, split `obj_list`.
    The return value is a list of these split lists.

    The function's behavior is undefined if `key_func` ever returns `None` (If
    you're tempted to return `None` anyways, read this statement as "Your code
    will break if `key_func` ever returns `None`").

    .. doctest::

       >>> def parity(x):
       ...     return x % 2
       >>> pprint(split_list(parity, [1, 3, 5, 2, 4, 7, 8, 9, 10]))
       [([1, 3, 5], Paginated(None, 1, 0)),
        ([2, 4], Paginated(1, 0, 1)),
        ([7], Paginated(0, 1, 0)),
        ([8], Paginated(1, 0, 1)),
        ([9], Paginated(0, 1, 0)),
        ([10], Paginated(1, 0, None))]
       >>> split_list(parity, [])
       []
       >>> split_list(parity, [1])
       [([1], Paginated(None, 1, None))]

    '''
    cur_list = obj_list
    nex_list = cur_list[1:] + [None]

    kprev = None

    ret = []
    acc = []
    for cur, nex in zip(cur_list, nex_list):
        kcur = cur and key_func(cur)
        knex = nex and key_func(nex)
        acc.append(cur)
        if kcur != knex:
            ret.append((acc, Paginated(kprev, kcur, knex)))
            kprev = kcur
            acc = []
    return ret


def paginate(num_per_page, obj_list):
    '''Break `obj_list` into lists of at most `num_per_page` objects.

        >>> pprint(paginate(1, [1, 2, 3, 4, 5, 6, 7]))
        [([1], Paginated(None, 1, 2)),
         ([2], Paginated(1, 2, 3)),
         ([3], Paginated(2, 3, 4)),
         ([4], Paginated(3, 4, 5)),
         ([5], Paginated(4, 5, 6)),
         ([6], Paginated(5, 6, 7)),
         ([7], Paginated(6, 7, None))]
        >>> pprint(paginate(2, [1, 2, 3, 4, 5, 6, 7]))
        [([1, 2], Paginated(None, 1, 2)),
         ([3, 4], Paginated(1, 2, 3)),
         ([5, 6], Paginated(2, 3, 4)),
         ([7], Paginated(3, 4, None))]
        >>> paginate(2, [])
        []
        >>> paginate(2, [1])
        [([1], Paginated(None, 1, None))]

    '''
    num_pages = (len(obj_list) + num_per_page - 1) / num_per_page

    prev_list = [None] + range(1, num_pages)
    cur_list  = range(1, num_pages + 1)
    nex_list  = range(2, num_pages + 1) + [None]

    ret = []
    for prev, cur, nex in zip(prev_list, cur_list, nex_list):
        begin = (cur - 1) * num_per_page
        end   = begin + num_per_page
        objs  = obj_list[begin:end]
        ret.append((objs, Paginated(prev, cur, nex)))
    return ret


def split_paginate(num_per_page, key_func, obj_list):
    '''Split `obj_list` with `split_list`; then use `paginate`.

    The lists will be split according to `split_list`.  Each of the
    resulting lists will then be passed to `paginate`.  The result will be
    a nested datastructure that is best explained by example.

    .. doctest::

       >>> def parity(x):
       ...     return x % 2
       >>> pprint(split_paginate(2, parity, [1, 3, 5, 7, 9, 2, 4, 7, 9, 10]))
       [([1, 3], Paginated(None, 1, 0), Paginated(None, 1, 2)),
        ([5, 7], Paginated(None, 1, 0), Paginated(1, 2, 3)),
        ([9], Paginated(None, 1, 0), Paginated(2, 3, None)),
        ([2, 4], Paginated(1, 0, 1), Paginated(None, 1, None)),
        ([7, 9], Paginated(0, 1, 0), Paginated(None, 1, None)),
        ([10], Paginated(1, 0, None), Paginated(None, 1, None))]
       >>> split_paginate(2, parity, [])
       []
       >>> split_paginate(2, parity, [1])
       [([1], Paginated(None, 1, None), Paginated(None, 1, None))]
       >>> pprint(split_paginate(2, parity, [1, 2]))
       [([1], Paginated(None, 1, 0), Paginated(None, 1, None)),
        ([2], Paginated(1, 0, None), Paginated(None, 1, None))]

    '''
    ret = []
    for split_obj, split_key in split_list(key_func, obj_list):
        for page_list, page_key in paginate(num_per_page, split_obj):
            ret.append((page_list, split_key, page_key))
    return ret
