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

        >>> p = Paginated(1, 2, 3)
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


def split_list_action(key_func, obj_list, action):
    '''Split obj_list at boundaries determined by key_func and call action.

    At each point the value of key_func changes, split obj_list.  Then for each
    new list, call action with the list, and the key values for prev/cur/next.

    The function's behavior is undefined if key_func ever returns None.

        >>> def parity(x):
        ...     return x % 2
        >>> def action(obj_list, groups):
        ...     print obj_list, groups.prev, groups.cur, groups.next
        >>> split_list_action(parity, [1, 3, 5, 2, 4, 7, 8, 9, 10], action)
        [1, 3, 5] None 1 0
        [2, 4] 1 0 1
        [7] 0 1 0
        [8] 1 0 1
        [9] 0 1 0
        [10] 1 0 None
        >>> split_list_action(parity, [], action)
        >>> split_list_action(parity, [1], action)
        [1] None 1 None

    '''
    cur_list = obj_list
    nex_list = cur_list[1:] + [None]

    kprev = None

    acc = list()
    for cur, nex in zip(cur_list, nex_list):
        kcur = cur and key_func(cur)
        knex = nex and key_func(nex)
        acc.append(cur)
        if kcur != knex:
            action(acc, Paginated(kprev, kcur, knex))
            kprev = kcur
            acc = list()


def paginate_action(num_per_page, obj_list, action):
    '''Call ``action`` with the prev/cur/next page numbers and an obj_list.

        >>> def action(obj_list, pages):
        ...     print obj_list, pages.prev, pages.cur, pages.next
        >>> paginate_action(1, [1, 2, 3, 4, 5, 6, 7], action)
        [1] None 1 2
        [2] 1 2 3
        [3] 2 3 4
        [4] 3 4 5
        [5] 4 5 6
        [6] 5 6 7
        [7] 6 7 None
        >>> paginate_action(2, [1, 2, 3, 4, 5, 6, 7], action)
        [1, 2] None 1 2
        [3, 4] 1 2 3
        [5, 6] 2 3 4
        [7] 3 4 None
        >>> paginate_action(2, [], action)
        >>> paginate_action(2, [1], action)
        [1] None 1 None

    '''
    num_pages = (len(obj_list) + num_per_page - 1) / num_per_page

    prev_list = [None] + range(1, num_pages)
    cur_list  = range(1, num_pages + 1)
    nex_list  = range(2, num_pages + 1) + [None]

    for prev, cur, nex in zip(prev_list, cur_list, nex_list):
        begin = (cur - 1) * num_per_page
        end   = begin + num_per_page
        objs  = obj_list[begin:end]
        action(objs, Paginated(prev, cur, nex))


def split_paginate_action(num_per_page, key_func, obj_list, action):
    '''Split obj_list with split_list_action; then use paginate_action.

    The lists will be split according to split_list_action.  Each of the
    resulting lists will then be passed to paginate_action.  The result will be
    the action callable will be called with arguments for the objects, the
    prev/cur/next keys from split_list_action, and the prev/cur/next keys from
    paginate_action (total of 7 args).

        >>> def parity(x):
        ...     return x % 2
        >>> def action(obj_list, groups, pages):
        ...     print obj_list, groups.prev, groups.cur, groups.next,
        ...     print pages.prev, pages.cur, pages.next
        >>> split_paginate_action(2, parity, [1, 3, 5, 7, 9, 2, 4, 7, 9, 10], action)
        [1, 3] None 1 0 None 1 2
        [5, 7] None 1 0 1 2 3
        [9] None 1 0 2 3 None
        [2, 4] 1 0 1 None 1 None
        [7, 9] 0 1 0 None 1 None
        [10] 1 0 None None 1 None
        >>> split_paginate_action(2, parity, [], action)
        >>> split_paginate_action(2, parity, [1], action)
        [1] None 1 None None 1 None
        >>> split_paginate_action(2, parity, [1, 2], action)
        [1] None 1 0 None 1 None
        [2] 1 0 None None 1 None

    '''
    def new_act_split_list(obj_list, groups):
        '''The action to pass to split_list_action.
        '''
        def new_act_paginate(obj_list, pages):
            '''The action to pass to paginate_action.
            '''
            action(obj_list, groups, pages)
        paginate_action(num_per_page, obj_list, new_act_paginate)
    split_list_action(key_func, obj_list, new_act_split_list)
