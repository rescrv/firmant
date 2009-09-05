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


class Category(AtomBase):

    fields    = ['term', 'label']
    __slots__ = fields

    @classmethod
    def by_term(cls, term):
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
