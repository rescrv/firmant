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


'''Sample objects as if the standard chunks have been called up to, but not
including, 900
'''


import datetime

import minimock
import pytz

from firmant import parsers


tz = pytz.timezone('America/New_York')


def __mockpub__(**kwargs):
    pub = minimock.Mock('__pub__')
    pub.writer = minimock.Mock('writer')
    pub.writer.parts = kwargs
    return pub


posts = []

posts.append(parsers.posts.Post())
posts[-1].author    = u'John Doe'
posts[-1].copyright = u'Same as source.'
posts[-1].feeds     = [u'foo', u'bar', u'baz', u'quux']
posts[-1].published = tz.localize(datetime.datetime(2009, 12, 31, 23, 59))
posts[-1].slug      = u'party'
posts[-1].tags      = [u'foo']
posts[-1].updated   = tz.localize(datetime.datetime(2009, 12, 31, 23, 59))
posts[-1].__pub__   = __mockpub__(fragment=u'<p>This is the content.</p>\n',
                                  title=u'Here Comes the New Year!')

posts.append(parsers.posts.Post())
posts[-1].author    = u'John Doe'
posts[-1].copyright = u'Same as source.'
posts[-1].feeds     = [u'foo', u'bar']
posts[-1].published = tz.localize(datetime.datetime(2010, 1, 1, 0, 0))
posts[-1].slug      = u'newyear'
posts[-1].tags      = [u'bar']
posts[-1].updated   = tz.localize(datetime.datetime(2010, 1, 1, 0, 0))
posts[-1].__pub__   = __mockpub__(fragment=u'<p>This is the content.</p>\n',
                                  title=u'Here Is the New Year!')

posts.append(parsers.posts.Post())
posts[-1].author    = u'John Doe'
posts[-1].copyright = u'Same as source.'
posts[-1].feeds     = [u'baz', u'quux']
posts[-1].published = tz.localize(datetime.datetime(2010, 2, 1, 0, 10))
posts[-1].slug      = u'newmonth'
posts[-1].tags      = [u'quux']
posts[-1].updated   = tz.localize(datetime.datetime(2010, 2, 1, 0, 10))
posts[-1].__pub__   = __mockpub__(title=u'Here Is a New Month!',
                    fragment=u'<p>This is the content of the new month.</p>\n')

posts.append(parsers.posts.Post())
posts[-1].author    = u'John Doe'
posts[-1].copyright = u'Same as source.'
posts[-1].feeds     = [u'baz', u'foo']
posts[-1].published = tz.localize(datetime.datetime(2010, 2, 2, 0, 10))
posts[-1].slug      = u'newday'
posts[-1].tags      = [u'baz', u'foo']
posts[-1].updated   = tz.localize(datetime.datetime(2010, 2, 2, 0, 10))
posts[-1].__pub__   = __mockpub__(title=u'Here Is a New Day!',
                    fragment=u'<p>This is the content of the new day.</p>\n')

posts.append(parsers.posts.Post())
posts[-1].author    = u'John Doe'
posts[-1].copyright = u'Same as source.'
posts[-1].feeds     = [u'baz', u'foo']
posts[-1].published = tz.localize(datetime.datetime(2010, 2, 2, 0, 10))
posts[-1].slug      = u'newday2'
posts[-1].tags      = [u'baz', u'foo']
posts[-1].updated   = tz.localize(datetime.datetime(2010, 2, 2, 0, 10))
posts[-1].__pub__   = __mockpub__(title=u'Here Is a New Day!',
            fragment=u'<p>This is the content of the new day (again).</p>\n')


static = []

static.append(parsers.static.StaticObject())
static[-1].relpath  = 'images/88x31.png'
static[-1].fullpath = 'testdata/pristine/static/images/88x31.png'


staticrst = []

staticrst.append(parsers.staticrst.StaticRstObject())
staticrst[-1].path      = u'about'
staticrst[-1].__pub__   = __mockpub__(title=u'About',
        html_body=u'<p>Firmant is an awesome content management system.</p>\n')

staticrst.append(parsers.staticrst.StaticRstObject())
staticrst[-1].path      = u'empty'
staticrst[-1].__pub__   = __mockpub__(title=u'About', html_body=u'')

staticrst.append(parsers.staticrst.StaticRstObject())
staticrst[-1].path      = u'links'
staticrst[-1].__pub__   = __mockpub__(title=u'About', html_body=
                          u'<ul class="simple">\n<li><a class="reference e' + \
                          u'xternal" href="http://firmant.org">Firmant</a>' + \
                          u'</li>\n<li><a class="reference external" href=' + \
                          u'"http://chasmd.org">CHASM</a></li>\n</ul>\n')


feeds = []

feeds.append(parsers.feeds.Feed())
feeds[-1].copyright = u''
feeds[-1].slug      = u'foo'
feeds[-1].posts     = [posts[0], posts[1], posts[3], posts[4]]
feeds[-1].__pub__   = __mockpub__(fragment=u'', title=u'Foo', subtitle=u'')

feeds.append(parsers.feeds.Feed())
feeds[-1].copyright = u''
feeds[-1].slug      = u'bar'
feeds[-1].posts     = [posts[0], posts[1]]
feeds[-1].__pub__   = __mockpub__(fragment=u'', title=u'Bar', subtitle=u'')

feeds.append(parsers.feeds.Feed())
feeds[-1].copyright = u''
feeds[-1].slug      = u'baz'
feeds[-1].posts     = [posts[0], posts[2], posts[3], posts[4]]
feeds[-1].__pub__   = __mockpub__(fragment=u'', title=u'Baz', subtitle=u'')

feeds.append(parsers.feeds.Feed())
feeds[-1].copyright = u''
feeds[-1].slug      = u'quux'
feeds[-1].posts     = [posts[0], posts[2]]
feeds[-1].__pub__   = __mockpub__(fragment=u'', title=u'Baz', subtitle=u'')

posts[0].feeds = [feeds[0], feeds[1], feeds[2], feeds[3]]
posts[1].feeds = [feeds[0], feeds[1]]
posts[2].feeds = [feeds[2], feeds[3]]
posts[3].feeds = [feeds[2], feeds[0]]
posts[4].feeds = [feeds[2], feeds[0]]


tags = []

tags.append(parsers.tags.Tag())
tags[-1].slug      = u'foo'
tags[-1].posts     = [posts[0], posts[3], posts[4]]
tags[-1].__pub__   = __mockpub__(fragment=u'', title=u'Foo', subtitle=u'')

tags.append(parsers.tags.Tag())
tags[-1].slug      = u'bar'
tags[-1].posts     = [posts[1]]
tags[-1].__pub__   = __mockpub__(fragment=u'', title=u'Bar', subtitle=u'')

tags.append(parsers.tags.Tag())
tags[-1].slug      = u'baz'
tags[-1].posts     = [posts[3], posts[4]]
tags[-1].__pub__   = __mockpub__(fragment=u'', title=u'Baz', subtitle=u'')

tags.append(parsers.tags.Tag())
tags[-1].slug      = u'quux'
tags[-1].posts     = [posts[2]]
tags[-1].__pub__   = __mockpub__(fragment=u'', title=u'Baz', subtitle=u'')


posts[0].tags = [tags[0]]
posts[1].tags = [tags[1]]
posts[2].tags = [tags[3]]
posts[3].tags = [tags[2], tags[0]]
posts[4].tags = [tags[2], tags[0]]
