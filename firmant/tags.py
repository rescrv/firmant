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


'''Manipulate tag objects for Firmant.
'''


import datetime
import os
import re

from firmant import du
from firmant import properties


__all__ = ['Tag', 'list_tags', 'parse_tag']


slug_re = re.compile('^[a-zA-Z0-9][-\\_a-zA-Z0-9]{1,30}[a-zA-Z0-9]$')


class Tag(object):
    '''A Tag object.

    It is the core of the tag manipulation functions.
    '''

    __slots__ = ['_slug', '_title', '_subtitle', '_copyright', '_updated'
                ,'_entries', '_body']

    def __init__(self, **kwargs):
        '''Construct a new Tag.  Optional kwargs are used to populate the data
        members.

            >>> # Create a new Tag object and specify all fields.
            >>> d = {'slug': 'rcos'
            ...     ,'title': 'RCOS'
            ...     ,'entries': list()
            ...     }
            >>> Tag(**d) #doctest: +ELLIPSIS
            <firmant.tags.Tag object at 0x...>

            >>> # KeyError will be thrown if invalid arguments are passed.
            >>> Tag(noexist=True)
            Traceback (most recent call last):
            KeyError: "Invalid key ''noexist'' found in kwargs."

        '''
        defaults = {'slug': None
                   ,'title': None
                   ,'entries': list()
                   }
        defaults.update(kwargs)
        for key, value in kwargs.items():
            if '_' + key not in self.__slots__:
                raise KeyError("Invalid key '%s' found in kwargs." % repr(key))
            else:
                setattr(self, key, value)

    slug = properties.property_regex('_slug', 'slug', slug_re,
    doc='''The slug property.

    Access to the slug is mediated to validate that the slug always contains a
    valid unicode object (or ``None``).

        >>> t = Tag()
        >>> t.slug
        >>> t.slug = u'rcos'
        >>> t.slug
        u'rcos'

        >>> # Assigning None will set the slug to None
        >>> t.slug = None
        >>> t.slug

        >>> # An invalid slug will raise a ValueError.
        >>> t = Tag()
        >>> t.slug = '_rcos'
        Traceback (most recent call last):
        ValueError: Invalid value for 'slug'.  Failed to match regex.

    ''')

    title = properties.property_unicode('_title', 'title',
    doc='''The title property.

    Access to the title is mediated to validate that the title always contains a
    valid unicode object (or ``None``).

        >>> t = Tag()
        >>> t.title
        >>> t.title = None
        >>> t.title

        >>> t = Tag(title='RCOS')
        >>> t.title
        u'RCOS'

        >>> t = Tag()
        >>> t.title = 'RCOS'
        >>> t.title
        u'RCOS'

    ''')

    entries = properties.property_iterable('_entries', 'entries',
    doc='''The entries property.

    Access to the entries is mediated to validate that the entries always
    contains a valid iterable object.

        >>> t = Tag()
        >>> t.entries
        []

        >>> # Assigning None simply empties the list.
        >>> t = Tag()
        >>> t.entries = None
        >>> t.entries
        []

        >>> t.entries = ['foo', 'bar', 'baz']
        >>> t.entries
        ['foo', 'bar', 'baz']

        >>> # Raise a TypeError when assigned a non-iterable.
        >>> t.entries = 1
        Traceback (most recent call last):
        TypeError: 'int' object is not iterable

    ''')


def list_tags(content_root, subdir='tags', suffix='.rst'):
    '''Generate the absolute path for each tag object.

    Consider all the contents of the tags directory (by default this is
    ``content_root/tags``).  Only files ending in ``suffix`` are considered.

    Entries that are not files are ignored.

        >>> list_tags('content')
        ['content/tags/empty.rst', 'content/tags/rcos.rst']

    '''

    path  = os.path.join(content_root, 'tags')
    files = os.listdir(path)
    files = map(lambda p: os.path.join(path, p), files)
    files = filter(lambda f: f.endswith(suffix), files)
    files = filter(lambda f: os.path.isfile(f), files)
    files.sort()
    return files


def parse_tag(path):
    '''Construct a tag object from the tag on the file system.

    This does not load any information other than that which is stored in the
    ``/tags/`` directory.

        >>> t = parse_tag('content/tags/rcos.rst')
        >>> t.slug
        u'rcos'
        >>> t.title
        u'Rensselaer Center for Open Source'
        >>> t.entries
        []

        >>> # Test the empty-file case.
        >>> t = parse_tag('content/tags/empty.rst')
        >>> t.slug
        u'empty'
        >>> t.title
        u''
        >>> t.entries
        []

    '''
    file = open(path)
    data = file.read()
    file.close()
    parts, doc = du.publish_parts_doc(data)

    t = Tag()
    t.slug = os.path.basename(path).rsplit('.', 1)[0]
    t.title = parts.get('title')
    return t
