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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import collections

import firmant.objects


'''Paginate or group objects according to certain attributes.
'''


class Paginated(object):

    def __init__(self, objects, prev, next):
        self._objects = objects
        self._prev_key = prev
        self._next_key = next
        self._prev_url = None
        self._next_url = None

    @property
    def prev(self):
        '''The URL of the previous list.
        '''
        return self._prev_url

    @property
    def next(self):
        '''The URL of the next list.
        '''
        return self._next_url


class PaginatedParser(object):

    def __init__(self, fix, retrieve, groupby, sortby=None):
        self._fix = fix
        self._retrieve = retrieve
        self._groupby = groupby
        self._sortby = sortby or tuple

    def iterate(self):
        group = collections.defaultdict(list)
        for key, obj in firmant.objects.retrieve(self._retrieve):
            d = dict((k, v) for k, v in key.iteritems() if k in self._groupby)
            d.update(self._fix)
            d = tuple(sorted(d.items()))
            group[d].append(obj)
        objects = sorted(group.items(), key=lambda x: self._sortby(dict(x[0])))
        prev_list = [None] + range(0, len(objects) - 1)
        cur_list  = range(0, len(objects))
        next_list = list(range(1, len(objects))) + [None]
        added = []
        for prev, obj, next in zip(prev_list, objects, next_list):
            prev_key = None
            if prev is not None:
                prev_key = objects[prev]
            next_key = None
            if next is not None:
                next_key = objects[next]
            key, obj = obj
            added.append(firmant.objects.add(dict(key), Paginated(obj, prev_key, next_key)))
        return not bool([x for x in added if x])
