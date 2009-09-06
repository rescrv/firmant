import datetime
import pytz
import re

from firmant.plugins import SingleProviderPlugin
from firmant.utils import not_implemented
from firmant.constants import isoformat
from firmant.utils import xml, \
                          RFC3339, \
                          strptime
from firmant.utils import json


# Base classes for Atom data.


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')


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


class Author(AtomBase):

    fields    = ['name', 'uri', 'email']
    __slots__ = fields

    # TODO:
    #def permalink(self):
    #    not_implemented()


class AtomAuthorProvider(SingleProviderPlugin):

    def by_name(self, name):
        not_implemented() # pragma: no cover


class Category(AtomBase):

    fields    = ['term', 'label']
    __slots__ = fields


class AtomCategoryProvider(SingleProviderPlugin):

    def by_term(self, term):
        not_implemented() # pragma: no cover

    # TODO:
    #def permalink(self):
    #    not_implemented()


class Entry(AtomBase):

    # In case a subclass overloads __slots__ we can still compare two Entry
    # objects.
    fields    = ['slug', 'published', 'author', 'category', 'rights', 'updated',
                 'title', 'content', 'summary', 'tz']
    __slots__ = fields


class AtomEntryProvider(SingleProviderPlugin):

    def for_feed(self, feedslug):
        not_implemented() # pragma: no cover

    def single(self, slug, year, month, day):
        not_implemented() # pragma: no cover

    def day(self, year, month, day):
        not_implemented() # pragma: no cover

    def month(self, year, month):
        not_implemented() # pragma: no cover

    def year(self, year):
        not_implemented() # pragma: no cover

    def recent(self):
        not_implemented() # pragma: no cover


class Feed(AtomBase):

    fields    = ['slug', 'title', 'rights', 'subtitle', 'updated', 'entries']
    __slots__ = fields


class AtomFeedProvider(SingleProviderPlugin):

    def by_slug(self, slug):
        not_implemented() # pragma: no cover

    def default(self):
        not_implemented() # pragma: no cover


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
