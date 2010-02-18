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


import collections
import sys

from firmant import entries
from firmant import feeds
from firmant import tags


def stderr_warn(message):
    print >>sys.stderr, '[warning]: %s' % str(message)


def stderr_error(message):
    print >>sys.stderr, '[error]: %s' % str(message)


def stdout_warn(message):
    print '[warning]: %s' % str(message)


def stdout_error(message):
    print '[error]: %s' % str(message)


class Blog(object):
    '''A complete representation of a blog.

    This class loads all content from the filesystem and validates
    cross-references issuing warnings where appropriate.

        >>> Blog('content', stdout_warn, stdout_error) #doctest: +ELLIPSIS
        [warning]: implicit tag speech
        [warning]: implicit tag patriotism
        [error]: Undefined feed patriotic-things
        [warning]: implicit tag generated
        [warning]: implicit tag code
        [warning]: implicit tag python
        [warning]: implicit tag firmant
        [error]: Undefined feed RCOS
        <firmant.parser.Blog object at 0x...>

    '''

    __slots__ = ['_feeds', '_tags', '_entries']

    def __init__(self, content_root, warn=stderr_warn, error=stderr_error):
        self._feeds   = _feeds   = dict()
        self._tags    = _tags    = dict()
        self._entries = _entries = list()

        _feeds['default'] = feeds.Feed(slug='default', title='Default Feed')

        for feed in feeds.list_feeds(content_root):
            feed = feeds.parse_feed(feed)
            if feed.slug in _feeds:
                error('Duplicate feed %s' % feed.slug)
            else:
                _feeds[feed.slug] = feed

        inserted_entries = collections.defaultdict(list)
        for entry in entries.list_entries(content_root):
            entry = entries.parse_entry(entry)
            if entry.slug in inserted_entries[entry.published.date()]:
                error('Duplicate entry %s %s' % \
                        (str(entry.published.date()), entry.slug))
            else:
                _entries.append(entry)
                inserted_entries[entry.published.date()].append(entry.slug)

        for tag in tags.list_tags(content_root):
            tag = tags.parse_tag(tag)
            if tag.slug in _tags:
                error('Duplicate tag %s' % tag.slug)
            else:
                _tags[tag.slug] = tag

        for entry in _entries:
            for i, tag in enumerate(entry.tags):
                if tag not in _tags:
                    t = tags.Tag()
                    t.slug = t.title = tag
                    _tags[t.slug] = t
                    warn('implicit tag %s' % tag)
                entry.tags[i] = _tags[tag]
                _tags[tag].entries.append(entry)
            for i, feed in enumerate(entry.feeds):
                if feed not in _feeds:
                    error('Undefined feed %s' % feed)
                else:
                    _feeds[feed].entries.append(entry)
                    entry.feeds[i] = _feeds[feed]
