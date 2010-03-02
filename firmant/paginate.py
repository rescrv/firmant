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


def paginate(per_page, obj_list):
    '''Return a list of objects, broken up into lists of size per_page.

        >>> from pprint import pprint
        >>> pprint(paginate(1, [1, 2, 3, 4, 5, 6, 7]))
        [(1, 7, 1, 1, [1]),
         (2, 7, 2, 2, [2]),
         (3, 7, 3, 3, [3]),
         (4, 7, 4, 4, [4]),
         (5, 7, 5, 5, [5]),
         (6, 7, 6, 6, [6]),
         (7, 7, 7, 7, [7])]
        >>> pprint(paginate(2, [1, 2, 3, 4, 5, 6, 7]))
        [(1, 4, 1, 2, [1, 2]),
         (2, 4, 3, 4, [3, 4]),
         (3, 4, 5, 6, [5, 6]),
         (4, 4, 7, 7, [7])]

    '''
    num_pages = (len(obj_list) + per_page - 1) / per_page

    ret = list()
    for page in range(num_pages):
        begin = page * per_page
        end   = begin + per_page
        objs  = obj_list[begin:end]
        end   = begin + len(objs)
        begin += 1
        ret.append( (page + 1, num_pages, begin, end, objs) )
    return ret


def split_boundary(key, obj_list):
    '''Split a list across boundaries where key(a) != key(b)

    Split the list at each point the numbers change from evens to odds::

        >>> from pprint import pprint
        >>> def key(x):
        ...     if x is None:
        ...         return None
        ...     return x % 2
        >>> pprint(split_boundary(key, [1, 3, 5, 2, 4, 7, 8, 9, 10]))
        [(1, [1, 3, 5]), (0, [2, 4]), (1, [7]), (0, [8]), (1, [9]), (0, [10])]
        >>> pprint(split_boundary(key, [1]))
        [(1, [1])]
        >>> pprint(split_boundary(key, []))
        []

    '''
    if len(obj_list) == 0:
        return []
    if len(obj_list) == 1:
        return [(key(obj_list[0]), obj_list)]

    new_objs = zip(obj_list, obj_list[1:] + [None])

    ret = list()
    tmp = list()
    for cur, next in new_objs:
        tmp.append(cur)
        if key(cur) != key(next):
            ret.append((key(cur), tmp))
            tmp = list()
    return ret
