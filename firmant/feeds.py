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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''Manage all feeds, adding objects, and associating them as necessary.
'''


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import datetime

import lxml.etree

import firmant.objects


__all__ = ['add', 'add_content', 'FeedWriter']


def _add_text_subelement(root, name, text):
    '''Add a subelement named `name` to `root` with `text` inside.
    '''
    new = lxml.etree.SubElement(root, name)
    new.text = text


def _rfc3339(dt):
    '''Render the datetime object `dt` properly accoring to RFC 3339.

    It works properly without the time zone.

    .. doctest::

       >>> dt = datetime.datetime(2010, 05, 02, 01, 02, 03)
       >>> rfc3339(dt)
       '2010-05-02T01:02:03Z'

    It works properly with the time zone.

    .. doctest::

       >>> import pytz
       >>> eastern = pytz.timezone('US/Eastern')
       >>> dt = eastern.localize(datetime.datetime(2010, 05, 02, 01, 02, 03))
       >>> rfc3339(dt)
       '2010-05-02T01:02:03-04:00'

    '''
    frmt_str = '%Y-%m-%dT%H:%M:%S'
    timestamp = dt.strftime(frmt_str)
    timezone  = dt.strftime('%z')
    if timezone != '':
        return timestamp + timezone[:-2] + ':' + timezone[-2:]
    else:
        return timestamp + 'Z'


class Feed(object):

    def __init__(self, title, subtitle):
        self.title = title
        self.subtitle = subtitle
        self._filters = []

    def add_content(self, retrieve, convert):
        self._filters.append((retrieve, convert))

    def entries(self):
        ents = {}
        for retrieve, convert in self._filters:
            for key, obj in firmant.objects.retrieve(retrieve):
                url = firmant.urls.url(key)
                key = tuple(sorted(key.items()))
                if key not in ents:
                    cobj = convert(obj)
                    cobj['url'] = url
                    ents[key] = cobj
        return ents.values()


class FeedWriter(object):

    def __init__(self, retrieve):
        self._retrieve = retrieve

    def urls(self):
        return set([firmant.urls.url(key) for key, obj in firmant.objects.retrieve(self._retrieve)])

    def write_all(self):
        for key, obj in firmant.objects.retrieve(self._retrieve):
            self.write(key, obj)

    def write(self, key, obj):
        url = firmant.urls.url(key)
        if url is None:
            raise RuntimeError("Cannot publish %s because there is no URL" % repr(key))
        feed = lxml.etree.Element('feed')
        feed.set('xmlns', 'http://www.w3.org/2005/Atom')
        _add_text_subelement(feed, 'id', url)
        _add_text_subelement(feed, 'generator', 'Firmant')
        _add_text_subelement(feed, 'title', obj.title)
        selflink = lxml.etree.SubElement(feed, 'link')
        selflink.set('href', url)
        selflink.set('rel', 'self')
        entries = sorted(obj.entries(), key=lambda e: (e['updated'], e['published']), reverse=True)[:10]
        updated = entries[0]['updated'] if entries else datetime.datetime.now()
        _add_text_subelement(feed, 'updated', _rfc3339(updated))
        for entry in entries:
            e = lxml.etree.SubElement(feed, 'entry')
            _add_text_subelement(e, 'title', entry['title'])
            _add_text_subelement(e, 'updated', _rfc3339(entry['updated']))
            _add_text_subelement(e, 'published', _rfc3339(entry['published']))
            author = lxml.etree.SubElement(e, 'author')
            _add_text_subelement(author, 'name', entry['author'])
            content      = lxml.etree.SubElement(e, 'content')
            content.text = entry['html']
            content.set('type', 'html')
            l_alt = lxml.etree.SubElement(e, 'link')
            l_alt.set('href', entry['url'])
            l_alt.set('rel', 'alternate')
            _add_text_subelement(e, 'id', entry['url'])
        data = lxml.etree.tostring(feed, pretty_print=True).encode('utf-8')
        firmant.output.write(key, data)


def add(slug, title, subtitle=None):
    k = {'feed': slug}
    existing = firmant.objects.retrieve(k)
    if existing:
        raise RuntimeError('Feed %s already exists' % repr(slug))
    f = Feed(title, subtitle)
    firmant.objects.add(k, f)


def add_content(slug, retrieve, convert):
    k = {'feed': slug}
    existing = firmant.objects.retrieve(k)
    if not existing:
        raise RuntimeError('Feed %s does not exist' % repr(slug))
    assert len(existing) == 1
    k, f = existing[0]
    f.add_content(retrieve, convert)
