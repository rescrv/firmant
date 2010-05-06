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


'''Render feed in the `Atom format
<http://www.atomenabled.org/developers/syndication/atom-format-spec.php>`_.

'''


import datetime

from lxml import etree

from firmant.utils import paths
from firmant.writers.feeds import FeedWriter


def add_text_subelement(root, name, text):
    '''Add a subelement named `name` to `root` with `text` inside.
    '''
    new = etree.SubElement(root, name)
    new.text = text


def rfc3339(dt):
    '''Render the datetime object `dt` properly accoring to rfc 3339.

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


class AtomFeed(FeedWriter):
    '''Write feeds in the Atom format.

    Uses :class:`firmant.writers.feeds.FeedWriter` to render feeds in Atom
    format with the extension ``atom``.

    .. doctest::

       >>> AtomFeed({}, {'feeds': objects.feeds}) #doctest: +ELLIPSIS
       <firmant.writers.atom.AtomFeed object at 0x...>

    '''

    extension = 'atom'

    def render(self, environment, path, feed_obj):
        '''Render the feed according to the Atom specification.
        '''
        feed = etree.Element('feed')
        feed.set('xmlns', 'http://www.w3.org/2005/Atom')

        add_text_subelement(feed, 'generator', 'Firmant')
        add_text_subelement(feed, 'title', feed_obj.title)
        add_text_subelement(feed, 'rights', feed_obj.copyright)
        updated = max([post.published for post in feed_obj.posts] +
                [datetime.datetime(1900, 01, 01)])
        add_text_subelement(feed, 'updated', rfc3339(updated))
        add_text_subelement(feed, 'id', feed_obj.permalink)
        link = etree.SubElement(feed, 'link')
        link.set('href', feed_obj.permalink)
        link.set('rel', 'self')

        for post_obj in feed_obj.posts:
            post = etree.SubElement(feed, 'entry')
            add_text_subelement(post, 'title', post_obj.title)
            add_text_subelement(post, 'updated', rfc3339(post_obj.updated))
            add_text_subelement(post, 'published', rfc3339(post_obj.published))

            author = etree.SubElement(post, 'author')
            add_text_subelement(author, 'name', post_obj.author)

            content      = etree.SubElement(post, 'content')
            content.text = post_obj.content
            content.set('type', 'html')

            l_alt = etree.SubElement(post, 'link')
            l_alt.set('href', post_obj.permalink)
            l_alt.set('rel', 'alternate')

            add_text_subelement(post, 'id', post_obj.permalink)
            add_text_subelement(post, 'rights', post_obj.copyright)

            for tag in post_obj.tags:
                category = etree.SubElement(post, 'category')
                category.set('term', tag.slug)
                category.set('label', tag.title)

        out    = paths.create_or_truncate(path)
        out.write(etree.tostring(feed).encode('utf-8'))
        out.flush()
        out.close()


def _setup(test):
    '''Setup the environment for tests.
    '''
    from testdata.chunks import c900
    test.globs['objects'] = c900
