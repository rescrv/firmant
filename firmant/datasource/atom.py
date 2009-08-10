import datetime
import pytz

from firmant.plugins import SingleProviderPlugin
from firmant.utils import not_implemented
from firmant.constants import isoformat
from firmant.utils import xml, \
                          RFC3339, \
                          strptime
from firmant.utils import json


# Base classes for Atom data.


class AtomBase(object):

    def __eq__(self, other):
        for field in self.fields:
            if hasattr(self, field) \
               and hasattr(other, field) \
               and getattr(self, field) != getattr(other, field):
                return False
            if hasattr(self, field) \
               and not hasattr(other, field):
                return False
            if not hasattr(self, field) \
               and hasattr(other, field):
                return False
        return True

    def __ne__(self, other):
        return not (self == other)

    @classmethod
    def cast(cls, other):
        ret = cls()
        for field in cls.fields:
            if hasattr(other, field):
                setattr(ret, field, getattr(other, field))
        return ret


class Author(AtomBase):

    fields    = ['name', 'uri', 'email']
    __slots__ = fields

    @classmethod
    def by_name(cls, name):
        not_implemented() # pragma: no cover

    # TODO:
    #def permalink(self):
    #    not_implemented()

    def to_xml(self):
        author = xml.etree.Element('author')
        xml.add_text_subelement(author, 'name', self.name)
        xml.add_text_subelement(author, 'uri', self.uri)
        xml.add_text_subelement(author, 'email', self.email)
        return author


class Category(AtomBase):

    fields    = ['term', 'label']
    __slots__ = fields

    @classmethod
    def by_term(cls, term):
        not_implemented() # pragma: no cover

    # TODO:
    #def permalink(self):
    #    not_implemented()

    def to_xml(self):
        category = xml.etree.Element('category')
        category.set('term', self.term)
        category.set('label', self.label)
        return category


class Entry(AtomBase):

    # In case a subclass overloads __slots__ we can still compare two Entry
    # objects.
    fields    = ['slug', 'published', 'author', 'category', 'rights', 'updated',
                 'title', 'content', 'summary', 'tz']
    __slots__ = fields

    @classmethod
    def for_feed(cls, feedslug):
        not_implemented() # pragma: no cover

    @classmethod
    def single(cls, slug, year, month, day):
        not_implemented() # pragma: no cover

    @classmethod
    def day(cls, year, month, day):
        not_implemented() # pragma: no cover

    @classmethod
    def month(cls, year, month):
        not_implemented() # pragma: no cover

    @classmethod
    def year(cls, year):
        not_implemented() # pragma: no cover

    @classmethod
    def recent(cls):
        not_implemented() # pragma: no cover

    @property
    def permalink(self):
        not_implemented() # pragma: no cover

    def to_xml(self, filter=None):
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

        xml.add_text_subelement(entry, 'title', self.title)
        xml.add_text_subelement(entry, 'updated', RFC3339(self.updated))
        xml.add_text_subelement(entry, 'published', RFC3339(self.published))
        author = self.author.to_xml()
        entry.append(author)

        content = xml.etree.SubElement(entry, 'content')
        content.set('type', 'xhtml')
        e = filter(self.content)
        content.append(e)

        l_alt = xml.etree.SubElement(entry, 'link')
        l_alt.set('href', self.permalink)
        l_alt.set('rel', 'alternate')

        xml.add_text_subelement(entry, 'id', self.permalink)
        xml.add_text_subelement(entry, 'rights', self.rights)

        summary = xml.etree.SubElement(entry, 'summary')
        summary.set('type', 'xhtml')
        e = filter(self.summary)
        summary.append(e)

        category = self.category.to_xml()
        entry.append(category)
        return entry


class Feed(AtomBase):

    fields    = ['slug', 'title', 'rights', 'subtitle', 'updated', 'entries']
    __slots__ = fields

    @classmethod
    def by_slug(cls, slug):
        not_implemented() # pragma: no cover

    @classmethod
    def default(cls):
        not_implemented() # pragma: no cover

    @property
    def permalink(self):
        not_implemented() # pragma: no cover

    def to_xml(self, filter=None):
        '''Convert a feed to XML.
        Filter should be a function that will convert content to a valid etree
        XML Element.'''

        feed = xml.etree.Element('feed')
        feed.set('xmlns', 'http://www.w3.org/2005/Atom')

        xml.add_text_subelement(feed, 'generator', 'Firmant')
        xml.add_text_subelement(feed, 'title', self.title)
        xml.add_text_subelement(feed, 'rights', self.rights)
        xml.add_text_subelement(feed, 'updated', RFC3339(self.updated))
        xml.add_text_subelement(feed, 'id', self.permalink)

        link = xml.etree.SubElement(feed, 'link')
        link.set('href', self.permalink)
        link.set('rel', 'self')

        for entry in self.entries:
            feed.append(entry.to_xml(filter))

        return feed


# Plugin Code


class AtomProvider(SingleProviderPlugin):

    provider_setting = 'ATOM_PROVIDER'

    entry    = property(lambda self: self._provider.entry,
                        doc="The Atom Entry class")

    feed     = property(lambda self: self._provider.feed,
                        doc="The Atom Feed class")

    author   = property(lambda self: self._provider.author,
                        doc="The Atom Author class")

    category = property(lambda self: self._provider.category,
                        doc="The Atom Category class")

    slug_re  = property(lambda self: self._provider.slug_re,
                        doc="The Atom slug re")


class EntryPermalinkProvider(SingleProviderPlugin):

    provider_setting = 'ENTRY_PERMALINK'

    def authoritative(self, slug, published):
        return self._provider.authoritative(slug, published)


class FeedPermalinkProvider(SingleProviderPlugin):

    provider_setting = 'FEED_PERMALINK'

    def authoritative(self, slug):
        return self._provider.authoritative(slug)
