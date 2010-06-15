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


'''Functions for interacting with the docutils module.

In particular this module makes creation of directives much more straightforward
and simple.  The :func:`meta_data_directive` produces a
:class:`MetaDataDirective`.  This result is suitable for registering with
:func:`docutils.parsers.rst.directives.register_directive`.

Docutils' processing is a multi-step process in which a module is read, parsed,
transformed, and written.  Each directive created with
:func:`meta_data_directive` creates a :class:`MetaDataNode` in the document tree
created by docutils.  When the custom :class:`CustomTransformReader` class is
used as the reader for docutils, and is passed :func:`meta_data_transform`
class, these nodes that contain metadata are then removed from the document
tree, and the metadata they store is added to the dictionary that the
:func:`meta_data_transform` is closed around.

'''


import functools
import re

from docutils import io
from docutils import core
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from docutils.transforms import Transform
from docutils.readers import standalone
from docutils import nodes

from firmant.utils import strptime


class MetaDataNode(nodes.Element, nodes.Invisible, nodes.Special):
    '''The MetaDataNode is a node that holds metadata for later Transforms.
    '''

    # pylint: disable-msg=R0904

    def __init__(self, details=None, rawsource='', *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)

        self.details = details or dict()


class URLAttributeNode(nodes.Element, nodes.Invisible, nodes.Special):
    '''The URLAttributeNode is a node that url attributes for a later transform.
    '''

    # pylint: disable-msg=R0904

    def __init__(self, extension, urlattributes, urltext, rawsource='',
                 *children, **attributes):
        nodes.Element.__init__(self, rawsource, *children, **attributes)

        self.extension = extension
        self.attributes = urlattributes
        self.urltext = urltext


def generic_reference_role(regex, typ, convert, role, rawtext, text, lineno,
        inliner, options=None, content=None):
    '''A generic reference role.

    It is designed to be curried with a regex, the type of link, and a function
    to return the extension, attributes, and urltext from the groupdict of the
    regex.
    '''
    options = options or {}
    content = content or []
    match   = re.match(regex, text)
    if match is None:
        err = _('Improper format for `%s` reference.') % typ
        msg = inliner.reporter.error(err, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    attributes = match.groupdict()
    extension, attributes, urltext = convert(attributes)
    return [URLAttributeNode(extension, attributes, urltext)], []


_feed_reference_role_re = r'^(?P<extension>\w{0,6}): ' + \
                          r'(?P<slug>(?:\||\-|\w)+)\s(?P<text>.+)$'
def _feed_reference_role_convert(attributes):
    '''Pull the necessary data from the attributes.
    '''
    ret = attributes.copy()
    ret['type'] = 'feed'
    extension = ret['extension']
    del ret['extension']
    urltext = ret['text']
    del ret['text']
    return extension, ret, urltext
feed_reference_role = functools.partial(generic_reference_role,
        _feed_reference_role_re, 'feed', _feed_reference_role_convert)
roles.register_local_role('feed', feed_reference_role)


_post_reference_role_re = r'^(?P<extension>\w{0,6}): (?P<year>[0-9]{4})-' + \
                          r'(?P<month>[0-9]{2})-(?P<day>[0-9]{2})\s' + \
                          r'(?P<slug>(?:\||\-|\w)+)\s(?P<text>.+)$'
def _post_reference_role_convert(attributes):
    '''Pull the necessary data from the attributes.
    '''
    ret = attributes.copy()
    for val in ('year', 'month', 'day'):
        ret[val] = int(ret[val], 10)
    ret['type'] = 'post'
    extension = ret['extension']
    del ret['extension']
    urltext = ret['text']
    del ret['text']
    return extension, ret, urltext
post_reference_role = functools.partial(generic_reference_role,
        _post_reference_role_re, 'post', _post_reference_role_convert)
roles.register_local_role('post', post_reference_role)


_static_reference_role_re = r'(?P<path>[-_?%/a-zA-Z0-9.]+)\s(?P<text>.+)$'
def _static_reference_role_convert(attributes):
    '''Pull the necessary data from the attributes.
    '''
    ret = attributes.copy()
    ret['type'] = 'static'
    urltext = ret['text']
    del ret['text']
    return None, ret, urltext
static_reference_role = functools.partial(generic_reference_role,
        _static_reference_role_re, 'static',
        _static_reference_role_convert)
roles.register_local_role('static', static_reference_role)


_staticrst_reference_role_re = r'^(?P<extension>\w{0,6}): ' + \
                               r'(?P<path>[-_?%/a-zA-Z0-9]+)\s(?P<text>.+)$'
def _staticrst_reference_role_convert(attributes):
    '''Pull the necessary data from the attributes.
    '''
    ret = attributes.copy()
    ret['type'] = 'staticrst'
    extension = ret['extension']
    del ret['extension']
    urltext = ret['text']
    del ret['text']
    return extension, ret, urltext
staticrst_reference_role = functools.partial(generic_reference_role,
        _staticrst_reference_role_re, 'staticrst',
        _staticrst_reference_role_convert)
roles.register_local_role('staticrst', staticrst_reference_role)


_tag_reference_role_re = r'^(?P<extension>\w{0,6}): ' + \
                          r'(?P<slug>(?:\||\-|\w)+)\s(?P<text>.+)$'
def _tag_reference_role_convert(attributes):
    '''Pull the necessary data from the attributes.
    '''
    ret = attributes.copy()
    ret['type'] = 'tag'
    extension = ret['extension']
    del ret['extension']
    urltext = ret['text']
    del ret['text']
    return extension, ret, urltext
tag_reference_role = functools.partial(generic_reference_role,
        _tag_reference_role_re, 'tag', _tag_reference_role_convert)
roles.register_local_role('tag', tag_reference_role)


def meta_data_directive(func, whitespace=False):
    '''Create a Directive class to store data to a MetaDataNode.

    The function ``func`` is passed the contents of the node and a dictionary
    into which it should place all relevant metadata it extracts from the
    contents.
    '''

    class MetaDataDirective(Directive):
        '''A generic directive for capturing metadata.
        '''

        required_arguments = 0
        optional_arguments = 0
        final_argument_whitespace = whitespace
        option_spec = dict()
        has_content = True

        def run(self):
            '''This will be called by the docutils parsing process.

            It calls `func` with an empty dictionary, and the content that falls
            under the scope of the directive.  It then replaces said content
            with a :class:`MetaDataNode`.

            If func encounters an error (and wishes to cleanly display it to the
            user), it should throw a :exc:`ValueError` that should be presented
            using the `str` function.  The error itself will not be included in
            the final document.

            '''
            # Raise an error if the directive does not have contents.
            self.assert_has_content()

            # Parse the contents into metadata.
            d = dict()
            try:
                func(d, self.content)
            except ValueError, ex:
                self.state_machine.reporter.error(str(ex))
                return []

            # Insert a MetaDataNode with the metadata.
            node = MetaDataNode(d)
            return [node]

    return MetaDataDirective


def copyright_declaration(d, content):
    r'''Interpret the content as a copyright declaration.

    .. doctest::

       >>> d = dict()
       >>> copyright_declaration(d, [u'foo', u'bar'])
       >>> d['copyright']
       u'foo\nbar'

    '''
    d['copyright'] = '\n'.join(content)


def time(d, content):
    '''Interpret the content as a time.

    There are multiple formats that are accepted.

    .. todo::

       Make the formats accepted integrate with the localization routines.

    Using just hours:

    .. doctest::

       >>> d = dict()
       >>> time(d, ['15'])
       >>> d['time']
       datetime.time(15, 0)

    Using hours and minutes:

    .. doctest::

       >>> d = dict()
       >>> time(d, ['15:43'])
       >>> d['time']
       datetime.time(15, 43)

    Using hours, minutes, and seconds:

    .. doctest::

       >>> d = dict()
       >>> time(d, ['15:43:42'])
       >>> d['time']
       datetime.time(15, 43, 42)

    ValueError is raised on invalid time:

    .. doctest::

       >>> d = dict()
       >>> time(d, ['154342'])
       Traceback (most recent call last):
       ValueError: time data '154342' does not match any format.

    '''
    formats = ['%H', '%H:%M', '%H:%M:%S']
    dt = strptime(''.join(content), formats)
    d['time'] = dt.time()


def single_line(d, content, attr='line'):
    '''Interpret the content as a single line.

    A single line of content passed to this function will be stored as `line` in
    the dictionary `d`.

    .. doctest::

       >>> d = dict()
       >>> single_line(d, [u'foobar'])
       >>> d['line']
       u'foobar'

    Optionally, the attribute may be specified so that multiple `single_line`
    directives can co-exist.

    .. doctest::

       >>> d = dict()
       >>> single_line(d, [u'foobar'], 'attr')
       >>> d['attr']
       u'foobar'

    '''
    d[attr] = unicode(''.join(content))


def updated(d, content):
    '''Interpret content as a full datetime.

    There are multiple formats that are accepted.

    .. todo::

       Make the formats accepted integrate with the localization routines.

    YYYY-MM-DD HH:MM:SS (time may be omitted):

    .. doctest::

       >>> d = dict()
       >>> updated(d, ['2009-02-01 14:15:51'])
       >>> d['updated']
       datetime.datetime(2009, 2, 1, 14, 15, 51)

       >>> updated(d, ['2009-02-01'])
       >>> d['updated']
       datetime.datetime(2009, 2, 1, 0, 0)

    MM-DD-YYYY HH:MM:SS (time may be omitted):

    .. doctest::

       >>> d = dict()
       >>> updated(d, ['02-01-2009 14:15:51'])
       >>> d['updated']
       datetime.datetime(2009, 2, 1, 14, 15, 51)

       >>> updated(d, ['02-01-2009'])
       >>> d['updated']
       datetime.datetime(2009, 2, 1, 0, 0)

    ValueError is raised on invalid datetime:

    .. doctest::

       >>> d = dict()
       >>> updated(d, ['154342'])
       Traceback (most recent call last):
       ValueError: time data '154342' does not match any format.

    '''
    formats = ['%Y-%m-%d', '%Y-%m-%d %H', '%Y-%m-%d %H:%M',
               '%Y-%m-%d %H:%M:%S', '%m-%d-%Y', '%m-%d-%Y %H',
               '%m-%d-%Y %H:%M', '%m-%d-%Y %H:%M:%S']
    d['updated'] = strptime(''.join(content), formats)


def list_element(d, content, attr='element_plural'):
    '''Interpret content as an element in a list.

    It returns a list so that the metadata transform can append values to the
    list.

    .. doctest::

       >>> d = dict()
       >>> list_element(d, [u'foo'])
       >>> d['element_plural']
       [u'foo']

    The key in which to store the values may be specified.

    .. doctest::

       >>> d = dict()
       >>> list_element(d, [u'foo'], 'attr')
       >>> d['attr']
       [u'foo']

    '''
    d[attr] = list([''.join(content)])


directives.register_directive('copyright',
    meta_data_directive(copyright_declaration, whitespace=True))

directives.register_directive('time', meta_data_directive(time))

directives.register_directive('timezone',
    meta_data_directive(lambda d, c: single_line(d, c, 'timezone')))

directives.register_directive('author',
    meta_data_directive(lambda d, c: single_line(d, c, 'author')))

directives.register_directive('updated', meta_data_directive(updated))

directives.register_directive('tag',
    meta_data_directive(lambda d, c: list_element(d, c, 'tags')))

directives.register_directive('feed',
    meta_data_directive(lambda d, c: list_element(d, c, 'feeds')))


def meta_data_transform(data):
    '''Create a docutils Transform that is a closure around the `data` dict.
    '''

    # pylint: disable-msg=R0903

    class MetaDataTransform(Transform):
        '''Remove MetaDataNode nodes and set attributes on document.
        '''
        default_priority = 700

        def apply(self):
            '''This will be called by the docutils parsing process.

            The `data` dictionary from :class:`meta_data_transform` will be
            populated with the items in the `details` attribute of each
            MetaDataNode encountered.

            '''
            for node in self.document.traverse(MetaDataNode):
                for key, val in node.details.items():
                    try:
                        iter(val)
                        if key in data:
                            val = data[key] + val
                    except TypeError:
                        pass
                    data[key] = val
                node.parent.remove(node)

    return MetaDataTransform


def url_node_transform(urlmapper):
    '''Create a docutils Transform that is a closure around the `urlmapper`
    object.
    '''

    class URLNodeTransform(Transform):
        '''Transform :class:`URLAttributeNode` into docutils references.
        '''

        # pylint: disable-msg=R0903
        # pylint: disable-msg=R0913

        default_priority = 600

        def apply(self):
            '''This will be called by the docutils parsing process.
            '''
            for node in self.document.traverse(URLAttributeNode):
                refuri  = urlmapper.url(node.extension, **node.attributes)
                newnode = nodes.reference(node.urltext, node.urltext,
                                          refuri=refuri)
                node.replace_self(newnode)

    return URLNodeTransform


class CustomTransformsReader(standalone.Reader):
    '''Add transformations to read MetaData from doctree.
    '''

    def __init__(self, parser=None, parser_name=None, transforms=None):
        standalone.Reader.__init__(self, parser, parser_name)
        self.transforms = transforms or []

    def get_transforms(self):
        '''Add a transform for moving the meta data into the data dictionary.
        '''
        return standalone.Reader.get_transforms(self) + self.transforms


def publish(path, transforms=None):
    '''Publish the rst document that resides at `path` on the filesystem.

    This function returns a :class:`docutils.core.Publisher` object.  The
    optional `transforms` attribute may be passed with a list of transform
    classes that will be passed to the reader.

    '''
    args = {'source': None
           ,'source_path': path
           ,'source_class': io.FileInput
           ,'destination_class': io.StringOutput
           ,'destination': None
           ,'destination_path': None
           ,'reader': CustomTransformsReader(transforms=transforms or [])
           ,'reader_name': None
           ,'parser': None, 'parser_name': 'restructuredtext'
           ,'writer': None, 'writer_name': 'html'
           ,'settings': None, 'settings_spec': None
           ,'settings_overrides': None
           ,'config_section': None
           ,'enable_exit_status': None
           }

    # Code borrowed from :mod:`docutils.core` from version 0.5 of docutils.
    # This is the implementation of the :func:`publish_programmatically`
    # function.  It is reimplemented so that it may be fractured into
    # transformation steps later.

    # From the module:
    # Author: David Goodger <goodger@python.org>
    # Copyright: This module has been placed in the public domain.

    pub = core.Publisher(args['reader'], args['parser'], args['writer'],
            settings=args['settings'],
            source_class=args['source_class'],
            destination_class=args['destination_class'])
    pub.set_components(args['reader_name'], args['parser_name'],
            args['writer_name'])
    pub.process_programmatic_settings( args['settings_spec'],
            args['settings_overrides'], args['config_section'])
    pub.set_source(args['source'], args['source_path'])
    pub.set_destination(args['destination'], args['destination_path'])
    pub.publish(enable_exit_status=args['enable_exit_status'])

    # End borrowed code.

    return pub
