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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''This documentation is for Firmant developers.  It assumes familiarity with
the user-level documentation (:ref:`_customizing_urls`).

Writer plugins specify the dictionary of attributes that define a rendered
object (typically an HTML document, but nothing enforces this).  This module
maps the dictionaries of attributes onto valid URLs and local filesystem paths
according to the URL rules provided by the user (either explicitly, or as part
of a package).  URLs are created by providing attributes to :func:`url`, while
local filesystem paths are created by providing attributes to :func:`fs`.

The way in which this works is best shown by example.  In the following
example, we first clear all URL routing rules, set the URL base, and
install a rule which matches HTML documents which represent ``post`` objects by
their ``year``, ``month``, ``day``, and ``slug``.  The example then constructs
a URL from a complete set of attributes.

.. doctest::

   >>> seturlbase('http://example.org/')
   >>> setfsbase('/tmp/firmant')
   >>> clear()
   >>> installrule(ext='html', fix={'type': 'post'},
   ...             fmt='/posts/{year:04}/{month:02}/{day:02}/{slug}')
   >>> a = {'type': 'post', 'year': 2011, 'month': 5, 'day': 19, 'slug': 'hi'}
   >>> url(a)  # We can pass a dictionary.
   u'http://example.org/posts/2011/05/19/hi/'
   >>> url(type='post', year=2011, month=5, day=19, slug='hi')  # Or use keywords.
   u'http://example.org/posts/2011/05/19/hi/'

By default, the :func:`installrule` function will create pretty URLs.  To do
so, it relies upon the web server to rewrite requests for directories to serve
an index document instead.  This behavior may be disabled on a per-rule or
global basis.  Per-rule pretty-URL settings override the global setting.
Compare the URLs and local filesystem paths in the following example.

.. doctest::

   >>> clear()
   >>> installrule(ext='html', fix={'type': 'post'},
   ...             fmt='/posts/{year:04}/{month:02}/{day:02}/{slug}')
   >>> installrule(ext='atom', fix={'type': 'atom'},
   ...             fmt='/atom/{slug}', pretty=True)
   >>> installrule(ext='rss', fix={'type': 'rss'},
   ...             fmt='/rss/{slug}', pretty=False)

   >>> url(type='post', year=2011, month=5, day=19, slug='hi')
   u'http://example.org/posts/2011/05/19/hi/'
   >>> fs(type='post', year=2011, month=5, day=19, slug='hi')
   u'/tmp/firmant/posts/2011/05/19/hi/index.html'

   >>> url(type='atom', slug='firmant')
   u'http://example.org/atom/firmant/'
   >>> fs(type='atom', slug='firmant')
   u'/tmp/firmant/atom/firmant/index.atom'

   >>> url(type='rss', slug='firmant')
   u'http://example.org/rss/firmant.rss'
   >>> fs(type='rss', slug='firmant')
   u'/tmp/firmant/rss/firmant.rss'

   >>> setpretty(False)  # A value of False globally disables pretty urls.

   >>> url(type='post', year=2011, month=5, day=19, slug='hi')
   u'http://example.org/posts/2011/05/19/hi.html'
   >>> fs(type='post', year=2011, month=5, day=19, slug='hi')
   u'/tmp/firmant/posts/2011/05/19/hi.html'

   >>> url(type='atom', slug='firmant')
   u'http://example.org/atom/firmant/'
   >>> fs(type='atom', slug='firmant')
   u'/tmp/firmant/atom/firmant/index.atom'

   >>> url(type='rss', slug='firmant')
   u'http://example.org/rss/firmant.rss'
   >>> fs(type='rss', slug='firmant')
   u'/tmp/firmant/rss/firmant.rss'

   >>> setpretty(True)  # A value of True globally enables pretty urls (the default).

   >>> url(type='post', year=2011, month=5, day=19, slug='hi')
   u'http://example.org/posts/2011/05/19/hi/'
   >>> fs(type='post', year=2011, month=5, day=19, slug='hi')
   u'/tmp/firmant/posts/2011/05/19/hi/index.html'

   >>> url(type='atom', slug='firmant')
   u'http://example.org/atom/firmant/'
   >>> fs(type='atom', slug='firmant')
   u'/tmp/firmant/atom/firmant/index.atom'

   >>> url(type='rss', slug='firmant')
   u'http://example.org/rss/firmant.rss'
   >>> fs(type='rss', slug='firmant')
   u'/tmp/firmant/rss/firmant.rss'

   >>> setpretty()  # Use the default pretty url behavior

:func:`url` and :func:`fs` will return ``None`` if no rule matches.

.. doctest::

   >>> url(type='notype')
   >>> fs(type='notype')

'''


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement

import os
import string
import urlparse


__all__ = ['seturlbase', 'clear', 'installrule', 'url', 'fs', 'setpretty']


# Internally, rules are stored as four-tuples:
# (ext, keys, fixed attributes, format string, pretty flag)


_PRETTYDEFAULT = True
_impl = {}
_rules = []
_impl['pretty'] = _PRETTYDEFAULT


def seturlbase(base):
    _impl['url'] = base


def setfsbase(base):
    _impl['fs'] = base


def clear():
    _rules = []


def installrule(ext, fix, fmt, pretty=None):
    keys = [x[1] for x in string.Formatter().parse(fmt) if x[1]]
    keys += fix.keys()
    keys = set(keys)
    _rules.append((ext, keys, fix, fmt, pretty))


def _first_matching_path(dicts, kwargs):
    '''Returns the information about the first matching rule.

    The information returned is the 4-tuple:
    (ext, fixed attributes, path, pretty flag)
    '''
    attr = {}
    for d in dicts:
        attr.update(d)
    attr.update(kwargs)
    keys = set(attr.keys())
    for ext, rule_keys, rule_fixed, fmt, pretty in _rules:
        fix = {}
        for key in rule_fixed.keys():
            fix[key] = attr[key]
        if keys == rule_keys and fix == rule_fixed:
            return ext, rule_fixed, fmt.format(**attr).rstrip('/'), pretty


def url(*dicts, **kwargs):
    match = _first_matching_path(dicts, kwargs)
    if not match:
        return None
    ext, fix, path, pretty = match
    if pretty or (pretty is None and _impl['pretty']):
        path += '/'
    else:
        path += '.%s' % ext
    return urlparse.urljoin(_impl['url'], path)


def fs(*dicts, **kwargs):
    match = _first_matching_path(dicts, kwargs)
    if not match:
        return None
    ext, fix, path, pretty = match
    path = path.lstrip('/')
    if pretty or (pretty is None and _impl['pretty']):
        path += '/index.%s' % ext
    else:
        path += '.%s' % ext
    return os.path.join(_impl['fs'], path)


def setpretty(pretty=None):
    if pretty is None:
        pretty = _PRETTYDEFAULT
    _impl['pretty'] = pretty
