import datetime
import pytz
import re

from firmant.datasource import Storage
from firmant.plugins import SingleProviderPlugin
from firmant.constants import isoformat
from firmant.utils import xml, \
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


class AtomAuthorProvider(SingleProviderPlugin, Storage):

    provider_setting = 'ATOM_AUTHOR_PROVIDER'

    def by_name(self, name):
        return self._provider.by_name(name)

    def exists(self, name):
        return self._provider.exists(name)

    def _save(self, obj):
        return self._provider._save(obj)

    def _delete(self, obj):
        return self._provider._delete(obj)


class Category(AtomBase):

    fields    = ['term', 'label']
    __slots__ = fields

    # TODO:
    #def permalink(self):
    #    not_implemented()


class AtomCategoryProvider(SingleProviderPlugin, Storage):

    provider_setting = 'ATOM_CATEGORY_PROVIDER'

    def by_term(self, term):
        return self._provider.by_term(term)

    def exists(self, term):
        return self._provider.exists(term)

    def _save(self, obj):
        return self._provider._save(obj)

    def _delete(self, obj):
        return self._provider._delete(obj)


class Entry(AtomBase):

    # In case a subclass overloads __slots__ we can still compare two Entry
    # objects.
    fields    = ['slug', 'published', 'author', 'category', 'rights', 'updated',
                 'title', 'content', 'summary', 'tz']
    __slots__ = fields


class AtomEntryProvider(SingleProviderPlugin):

    provider_setting = 'ATOM_ENTRY_PROVIDER'

    def for_feed(self, feedslug, limit=None, offset=None):
        return self._provider.for_feed(feedslug, limit, offset)

    def single(self, slug, year, month, day):
        return self._provider.single(slug, year, month, day)

    def exists(self, slug, year, month, day):
        return self._provider.exists(slug, year, month, day)

    def day(self, year, month, day, limit=None, offset=None):
        return self._provider.day(year, month, day, limit, offset)

    def month(self, year, month, limit=None, offset=None):
        return self._provider.month(year, month, limit, offset)

    def year(self, year, limit=None, offset=None):
        return self._provider.year(year, limit, offset)

    def recent(self, limit=None, offset=None):
        return self._provider.recent(limit, offset)

    def list(self):
        return self._provider.list()

    def list_years(self):
        return self._provider.list_years()

    def list_months(self):
        return self._provider.list_months()

    def list_days(self):
        return self._provider.list_days()


class Feed(AtomBase):

    fields    = ['slug', 'title', 'rights', 'subtitle', 'updated', 'entries']
    __slots__ = fields


class AtomFeedProvider(SingleProviderPlugin):

    provider_setting = 'ATOM_FEED_PROVIDER'

    def by_slug(self, slug):
        return self._provider.by_slug(slug)

    def exists(self, slug):
        return self._provider.exists(slug)

    def default(self):
        return self._provider.default()


# Plugin Code


class AtomProvider(object):

    def __init__(self, rc, settings):
        inst_rc       = rc()
        self.entry    = inst_rc.get(AtomEntryProvider)
        self.feed     = inst_rc.get(AtomFeedProvider)
        self.author   = inst_rc.get(AtomAuthorProvider)
        self.category = inst_rc.get(AtomCategoryProvider)


class EntryPermalinkProvider(SingleProviderPlugin):

    provider_setting = 'ENTRY_PERMALINK'

    def authoritative(self, slug, published):
        return self._provider.authoritative(slug, published)


class FeedPermalinkProvider(SingleProviderPlugin):

    provider_setting = 'FEED_PERMALINK'

    def authoritative(self, slug):
        return self._provider.authoritative(slug)
