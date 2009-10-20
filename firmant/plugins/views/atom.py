from werkzeug import Response

from firmant.views.generic import GenericFeedViewProvider
from firmant.filters import FilterProvider
from firmant.utils import xml
from firmant.utils import RFC3339


class AtomFeedPermalinkProvider(object):

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def authoritative(self, slug):
        endpoint = __name__ + '.AtomFeedViewProvider.'
        values = {}
        if slug == '':
            endpoint += 'default'
        else:
            endpoint += 'named'
            values['slug']  = slug

        urls = self.rc().get('urls')
        return urls.build(endpoint, values, force_external=True)


class AtomFeedViewProvider(GenericFeedViewProvider):

    @property
    def prefix(self):
        return self.settings.get('VIEW_ATOM_FEED_PREFIX', '')

    def render(self, request, feed):
        rc = self.rc()
        fp = rc.get(FilterProvider)
        def filter(content):
            open_div = '<div xmlns="http://www.w3.org/1999/xhtml">'
            close_div = '</div>'
            filtered_content = fp.filter('XHTML', content)
            return xml.etree.fromstring(open_div + filtered_content + close_div)
        content = xml.etree.tostring(feed_to_xml(feed, filter))
        return Response(content, mimetype='application/atom+xml')


def author_to_xml(author_obj):
    author = xml.etree.Element('author')
    xml.add_text_subelement(author, 'name',  author_obj.name)
    xml.add_text_subelement(author, 'uri',   author_obj.uri)
    xml.add_text_subelement(author, 'email', author_obj.email)
    return author


def category_to_xml(category_obj):
    category = xml.etree.Element('category')
    category.set('term',  category_obj.term)
    category.set('label', category_obj.label)
    return category


def entry_to_xml(entry_obj, filter=None):
    '''Convert an entry to XML.
    Filter should be a function that will convert content to a valid etree
    XML Element.'''

    if filter is None:
        def filter(content):
            ret = xml.etree.Element('div')
            ret.set('xmlns', 'http://www.w3.org/1999/xhtml')
            ret.text = content
            return ret
    entry = xml.etree.Element('entry')

    xml.add_text_subelement(entry, 'title',     entry_obj.title)
    xml.add_text_subelement(entry, 'updated',   RFC3339(entry_obj.updated))
    xml.add_text_subelement(entry, 'published', RFC3339(entry_obj.published))
    author = author_to_xml(entry_obj.author)
    entry.append(author)

    content = xml.etree.SubElement(entry, 'content')
    content.set('type', 'xhtml')
    e = filter(entry_obj.content)
    content.append(e)

    l_alt = xml.etree.SubElement(entry, 'link')
    l_alt.set('href', entry_obj.permalink)
    l_alt.set('rel', 'alternate')

    xml.add_text_subelement(entry, 'id', entry_obj.permalink)
    xml.add_text_subelement(entry, 'rights', entry_obj.rights)

    summary = xml.etree.SubElement(entry, 'summary')
    summary.set('type', 'xhtml')
    e = filter(entry_obj.summary)
    summary.append(e)

    category = category_to_xml(entry_obj.category)
    entry.append(category)
    return entry


def feed_to_xml(feed_obj, filter=None):
    '''Convert a feed to XML.
    Filter should be a function that will convert content to a valid etree
    XML Element.'''

    feed = xml.etree.Element('feed')
    feed.set('xmlns', 'http://www.w3.org/2005/Atom')

    xml.add_text_subelement(feed, 'generator', 'Firmant')
    xml.add_text_subelement(feed, 'title', feed_obj.title)
    xml.add_text_subelement(feed, 'rights', feed_obj.rights)
    xml.add_text_subelement(feed, 'updated', RFC3339(feed_obj.updated))
    xml.add_text_subelement(feed, 'id', feed_obj.permalink)

    link = xml.etree.SubElement(feed, 'link')
    link.set('href', feed_obj.permalink)
    link.set('rel', 'self')

    for entry in feed_obj.entries:
        feed.append(entry_to_xml(entry, filter))

    return feed
