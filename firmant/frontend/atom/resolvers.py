import datetime
import re
import urlparse
import lxml.etree as etree
import pytz

from firmant.wsgi import Response
from firmant.resolvers import Resolver
from firmant.backend.atom import AtomProvider
from firmant.filters import text_filter
from firmant.configuration import settings


atom_date_str = '%Y-%m-%dT%H:%M:%S%z'


def RFC3339(dt):
    ret = dt.strftime(atom_date_str)
    return ret[:-2] + ':' + ret[-2:]


def feed_permalink(slug=''):
    url = urlparse.urljoin(settings['HOST'], '/atom/')
    if slug != '':
        url += slug + '/'
    return url


class AtomResolver(Resolver):

    def __init__(self, prefix=''):
        if prefix == '':
            prefix = '^/'
        else:
            prefix = '^/' + prefix + '/'
        self.named_re = re.compile(prefix + '(?P<slug>[-_a-zA-Z0-9]{1,96})/$')
        self.default_re = re.compile(prefix + '$')

    def resolve(self, request):
        default = self.default_re.match(request.url)
        named = self.named_re.match(request.url)
        feed = None
        if default != None:
            feed = AtomProvider.feed()
            feed.title = settings['ATOM_DEFAULT_TITLE']
            feed.rights = settings['ATOM_DEFAULT_RIGHTS']
            feed.subtitle = settings['ATOM_DEFAULT_SUBTITLE']
            feed.entries = AtomProvider.entry.recent()
            feed.updated = pytz.utc.localize(
                    datetime.datetime(1900, 1, 1, 1, 1, 1))
            for entry in feed.entries:
                if feed.updated < entry.updated:
                    feed.updated = entry.updated
        elif named != None:
            feed = AtomProvider.feed.by_name(named.groupdict()['slug'])
        if feed == None:
            return None
        else:
            return Response(content=create_xml_from_feed(feed))


def create_xml_from_feed(feed):
    root = etree.Element('feed')
    root.set('xmlns', 'http://www.w3.org/2005/Atom')

    generator = etree.SubElement(root, 'generator')
    generator.text = settings['GENERATOR']

    title = etree.SubElement(root, 'title')
    title.text = feed.title

    rights = etree.SubElement(root, 'rights')
    rights.text = feed.rights

    updated = etree.SubElement(root, 'updated')
    updated.text = RFC3339(feed.updated)

    l_self = etree.SubElement(root, 'link')
    l_self.set('href', feed_permalink())
    l_self.set('rel', 'self')

    id = etree.SubElement(root, 'id')
    id.text = feed_permalink()

    for entry in feed.entries:
        root.append(create_xml_from_entry(entry))
    return ('<?xml version="1.0" encoding="utf-8"?>\n' +
            etree.tostring(root, pretty_print=True))

open_div = '<div xmlns="http://www.w3.org/1999/xhtml">'

def create_xml_from_entry(entry):
    root = etree.Element('entry')

    title = etree.SubElement(root, 'title')
    title.text = entry.title

    updated = etree.SubElement(root, 'updated')
    updated.text = RFC3339(entry.updated)

    published = etree.SubElement(root, 'published')
    published.text = RFC3339(entry.published)

    author = etree.SubElement(root, 'author')
    author_name = etree.SubElement(author, 'name')
    author_name.text = entry.author_name
    author_uri = etree.SubElement(author, 'uri')
    author_uri.text = entry.author_uri
    author_email = etree.SubElement(author, 'email')
    author_email.text = entry.author_email

    content = etree.SubElement(root, 'content')
    content.set('type', 'xhtml')
    e = etree.fromstring(open_div + text_filter('XHTML', entry.content) +'</div>')
    content.append(e)

    l_alt = etree.SubElement(root, 'link')
    l_alt.set('href', entry.permalink())
    l_alt.set('rel', 'alternate')

    id = etree.SubElement(root, 'id')
    id.text = entry.permalink()

    rights = etree.SubElement(root, 'rights')
    rights.text = entry.rights

    summary = etree.SubElement(root, 'summary')
    summary.set('type', 'xhtml')
    e = etree.fromstring(open_div + text_filter('XHTML', entry.summary) +'</div>')
    summary.append(e)

    category = etree.SubElement(root, 'category')
    category.set('term', entry.category_term)
    category.set('label', entry.category_label)
    return root
