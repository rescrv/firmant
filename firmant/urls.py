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

'''This module automatically handles URL construction.

Each URL in Firmant has two distinct locations associated with it.  The first
location is the location in the local filesystem hierarchy.  This location is
where Firmant applications write the generate website.  The other location is
the URL at which the generated website is published.  Firmant abstracts away
knowledge of these two locations behind a common interface.

The abstraction provided by this module is a set of rules which map key-value
attributes to local and remote path names.  The developer of a Firmant-powered
website may override these rules, and specify custom rules to tailor her URLs
without requiring any changes to the code which generates the URLs.

There is more to this module than meets the eye.  URLs come in two forms: the
first of which is standard for static websites and includes the file extension
(e.g., ``http://example.org/page.html``), while the second is the *pretty* form
of the URL and hides the extension (e.g., ``http://example.org/page/``).  The
second form of URLs requires that the webserver support serving index pages when
a request for a directory is made.
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


class BadRule(Exception): pass


def seturlbase(base):
    '''Set the base component of the URL.

    This is the address at which the published website will be accessible.

    .. doctest::

       >>> seturlbase('http://example.org/')

    '''
    _impl['url'] = base


def setfsbase(base):
    '''Set the base component for local filesystem paths.

    This is the local directory in which the website is built.

    .. doctest::

       >>> setfsbase('/var/www/example.org/')

    '''
    _impl['fs'] = base


def clear():
    '''Clear all installed rules.

    .. doctest::

       >>> clear()

    '''
    _rules = []


def installrule(ext, fix, fmt, pretty=None):
    '''Install a rule for constructing URLs.

    Each rule has three pieces:  the extension, the fixed attributes, and the
    format string which constructs the URL.  Each URL is constructed from a set
    of key-value pairs which identify the object.  When a rule is installed, the
    set of keys is inferred from the union of the keys of fixed attributes, and
    the keys defined by the format string.

    In the following example, the installed rule will match objects which have
    an attribute ``type`` which equals 'post', and attributes ``year``,
    ``month``, ``day``, and ``slug``.

    .. doctest::

       >>> installrule(ext='html', fix={'type': 'post'},
       ...             fmt='/posts/{year:04}/{month:02}/{day:02}/{slug}')
       ...

    '''
    if ext is None and pretty is not False:
        raise BadRule("URL rules with ext=None must set pretty=False")
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
            class WillNotMatch(object): pass
            fix[key] = attr.get(key, WillNotMatch)
        if keys == rule_keys and fix == rule_fixed:
            return ext, rule_fixed, fmt.format(**attr).rstrip('/'), pretty


def url(*dicts, **kwargs):
    '''Return the URL for the specified attributes.

    Firmant determines the URL for a set of attributes by finding the first rule
    which contains exactly the same set of attributes and which matches the
    fixed attributes specified by the rule.

    For instance, if we install the following rules:

    .. doctest::
       :hide:

       >>> seturlbase('https://URLBASE')
       >>> setpretty(True)
       >>> clear()

    .. doctest::

       >>> installrule(ext='html', fix={'type': 'wiki'}, fmt='/path/to/wiki/{url}')
       >>> installrule(ext='html', fix={}, fmt='/{type}/{url}')

    The rules will match only the attributes ``{'type', 'url'}``.  If ``type``
    is 'wiki', then the first rule will be used; otherwise, the second rule is
    used:

    .. doctest::

       >>> url(type='wiki', url='url/of/wiki/page')
       u'https://URLBASE/path/to/wiki/url/of/wiki/page/'
       >>> url(type='image', url='url/of/image')
       u'https://URLBASE/image/url/of/image/'

    If the rules do not match anything, then ``None`` is returned.

    .. doctest::

       >>> url(type='notype')

    When pretty URLs are enabled (the default), you get output like the above.
    If, however, pretty URLs are disabled, the output is different:

    .. doctest::

       >>> setpretty(False)
       >>> url(type='wiki', url='url/of/wiki/page')
       u'https://URLBASE/path/to/wiki/url/of/wiki/page.html'
       >>> url(type='image', url='url/of/image')
       u'https://URLBASE/image/url/of/image.html'

    For convenience, this function also accepts dictionaries instead of
    keyword attributes.

    .. doctest::

       >>> url({'type': 'wiki', 'url': 'url/of/wiki/page'})
       u'https://URLBASE/path/to/wiki/url/of/wiki/page.html'

    '''
    match = _first_matching_path(dicts, kwargs)
    if not match:
        return None
    ext, fix, path, pretty = match
    if pretty or (pretty is None and _impl['pretty']):
        path += '/'
    elif ext is not None:
        path += '.%s' % ext
    return urlparse.urljoin(_impl['url'], path)


def fs(*dicts, **kwargs):
    '''Return the filesystem path for the specified attributes.

    Firmant determines the filesystem path for a set of attributes by finding
    the first rule which contains exactly the same set of attributes and which
    matches the fixed attributes specified by the rule.

    For instance, if we install the following rules:

    .. doctest::
       :hide:

       >>> setfsbase('FSBASE')
       >>> clear()

    .. doctest::

       >>> installrule(ext='html', fix={'type': 'wiki'}, fmt='/path/to/wiki/{url}')
       >>> installrule(ext='html', fix={}, fmt='/{type}/{url}')

    The rules will match only the attributes ``{'type', 'url'}``.  If ``type``
    is 'wiki', then the first rule will be used; otherwise, the second rule is
    used:

    .. doctest::

       >>> fs(type='wiki', url='url/of/wiki/page')
       u'FSBASE/path/to/wiki/url/of/wiki/page/index.html'
       >>> fs(type='image', url='url/of/image')
       u'FSBASE/image/url/of/image/index.html'

    If the rules do not match anything, then ``None`` is returned.

    .. doctest::

       >>> fs(type='notype')

    When pretty URLs are enabled (the default), you get output like the above.
    If, however, pretty URLs are disabled, the output is different:

    .. doctest::

       >>> setpretty(False)
       >>> fs(type='wiki', url='url/of/wiki/page')
       u'FSBASE/path/to/wiki/url/of/wiki/page.html'
       >>> fs(type='image', url='url/of/image')
       u'FSBASE/image/url/of/image.html'

    For convenience, this function also accepts dictionaries instead of
    keyword attributes.

    .. doctest::

       >>> fs({'type': 'wiki', 'url': 'url/of/wiki/page'})
       u'FSBASE/path/to/wiki/url/of/wiki/page.html'

    '''
    match = _first_matching_path(dicts, kwargs)
    if not match:
        return None
    ext, fix, path, pretty = match
    path = path.lstrip('/')
    if pretty or (pretty is None and _impl['pretty']):
        path += '/index.%s' % ext
    elif ext is not None:
        path += '.%s' % ext
    return os.path.join(_impl['fs'], path)


def setpretty(pretty=None):
    '''

    By default, the :func:`installrule` function will create pretty URLs.  To do
    so, it relies upon the web server to rewrite requests for directories to
    serve an index document instead.  This behavior may be disabled on a
    per-rule or global basis.  Per-rule pretty-URL settings override the global
    setting.  Compare the URLs and local filesystem paths in the following
    example.

    .. doctest::

       >>> clear()
       >>> setfsbase('/var/www/example.org/')
       >>> seturlbase('http://example.org/')
       >>> installrule(ext='html', fix={'type': 'post'},
       ...             fmt='/posts/{year:04}/{month:02}/{day:02}/{slug}')
       >>> installrule(ext='atom', fix={'type': 'atom'},
       ...             fmt='/atom/{slug}', pretty=True)
       >>> installrule(ext='rss', fix={'type': 'rss'},
       ...             fmt='/rss/{slug}', pretty=False)

       >>> setpretty()  # Use the default pretty url behavior

       >>> url(type='post', year=2011, month=5, day=19, slug='hi')
       u'http://example.org/posts/2011/05/19/hi/'
       >>> fs(type='post', year=2011, month=5, day=19, slug='hi')
       u'/var/www/example.org/posts/2011/05/19/hi/index.html'

       >>> url(type='atom', slug='firmant')
       u'http://example.org/atom/firmant/'
       >>> fs(type='atom', slug='firmant')
       u'/var/www/example.org/atom/firmant/index.atom'

       >>> url(type='rss', slug='firmant')
       u'http://example.org/rss/firmant.rss'
       >>> fs(type='rss', slug='firmant')
       u'/var/www/example.org/rss/firmant.rss'

       >>> setpretty(False)  # A value of False globally disables pretty urls.

       >>> url(type='post', year=2011, month=5, day=19, slug='hi')
       u'http://example.org/posts/2011/05/19/hi.html'
       >>> fs(type='post', year=2011, month=5, day=19, slug='hi')
       u'/var/www/example.org/posts/2011/05/19/hi.html'

       >>> url(type='atom', slug='firmant')
       u'http://example.org/atom/firmant/'
       >>> fs(type='atom', slug='firmant')
       u'/var/www/example.org/atom/firmant/index.atom'

       >>> url(type='rss', slug='firmant')
       u'http://example.org/rss/firmant.rss'
       >>> fs(type='rss', slug='firmant')
       u'/var/www/example.org/rss/firmant.rss'

       >>> setpretty(True)  # A value of True globally enables pretty urls (the default).

       >>> url(type='post', year=2011, month=5, day=19, slug='hi')
       u'http://example.org/posts/2011/05/19/hi/'
       >>> fs(type='post', year=2011, month=5, day=19, slug='hi')
       u'/var/www/example.org/posts/2011/05/19/hi/index.html'

       >>> url(type='atom', slug='firmant')
       u'http://example.org/atom/firmant/'
       >>> fs(type='atom', slug='firmant')
       u'/var/www/example.org/atom/firmant/index.atom'

       >>> url(type='rss', slug='firmant')
       u'http://example.org/rss/firmant.rss'
       >>> fs(type='rss', slug='firmant')
       u'/var/www/example.org/rss/firmant.rss'

   '''
    if pretty is None:
        pretty = _PRETTYDEFAULT
    _impl['pretty'] = pretty
