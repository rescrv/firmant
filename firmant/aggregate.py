# Copyright (c) 2012, Robert Escriva
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
import firmant.urls


'''Group objects by their attributes'''


class Aggregate(object):

    def __init__(self, objects, prev, next):
        self.objects = objects
        self._prev = prev
        self._next = next
        self._prev_url = None
        self._next_url = None

    @property
    def prev(self):
        if self._prev is not None and self._prev_url is None:
            self._prev_url = firmant.urls.url(self._prev)
        return self._prev_url

    @property
    def next(self):
        if self._next is not None and self._next_url is None:
            self._next_url = firmant.urls.url(self._next)
        return self._next_url


class AggregateParser(object):

    def __init__(self, fix, retrieve, groupby, paginate=None, sortby=None, reverse=False):
        self._fix = fix
        self._retrieve = retrieve
        self._groupby = groupby
        self._sortby = sortby
        self._paginate = paginate or None
        self._reverse = reverse

    def iterate(self):
        group = collections.defaultdict(list)
        def sortfunc(obj):
            d = dict(obj[0])
            return tuple([d.get(s, None) for s in self._sortby or tuple(sorted(d.keys()))])
        for key, obj in sorted(firmant.objects.retrieve(self._retrieve), key=sortfunc, reverse=self._reverse):
            d = dict((k, v) for k, v in key.iteritems() if k in self._groupby)
            d.update(self._fix)
            d = tuple(sorted(d.items()))
            group[d].append(obj)
        objects = sorted(group.items(), key=sortfunc, reverse=self._reverse)
        if not objects:
            return True
        if self._paginate is not None:
            objects = self._paginated(objects)
        prev_list = [(None, None)] + objects[:-1]
        cur_list  = objects
        next_list = objects[1:] + [(None, None)]
        for prev, obj, next in zip(prev_list, objects, next_list):
            firmant.objects.add(dict(obj[0]), Aggregate(obj[1], prev[0], next[0]))
        return True

    def _paginated(self, objects):
        p = self._paginate
        split_objects = []
        for obj in objects:
            pieces = [(obj[0], obj[1][i:i+p]) for i in range(0, len(obj[1]), p)]
            for i in range(len(pieces)):
                a, b = pieces[i]
                a = dict(a)
                a['page'] = i + 1
                pieces[i] = (a, b)
            split_objects += pieces
        return split_objects
