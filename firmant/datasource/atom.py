import datetime

from firmant.plugins import PluginMount
from firmant.utils import not_implemented


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
        return not __eq__(self, other)


class Entry(AtomBase):

    # In case a subclass overloads __slots__ we can still compare two Entry
    # objects.
    fields    = ['slug', 'published', 'author', 'category', 'rights', 'updated',
                 'title', 'content', 'summary', 'tz']
    __slots__ = fields

    @classmethod
    def for_feed(cls, feedslug, count=10, offset=0):
        not_implemented()

    @classmethod
    def single(cls, slug, date):
        not_implemented()

    @classmethod
    def day(cls, year, month, day, count=10, offset=0):
        not_implemented()

    @classmethod
    def month(cls, year, month, count=10, offset=0):
        not_implemented()

    @classmethod
    def year(cls, year, count=10, offset=0):
        not_implemented()

    @classmethod
    def recent(cls, count=10, offset=0):
        not_implemented()

    def permalink(self):
        not_implemented()


class Feed(AtomBase):

    fields    = ['slug', 'title', 'rights', 'subtitle', 'updated']
    __slots__ = fields

    @classmethod
    def by_slug(cls, slug):
        not_implemented()

    @classmethod
    def default(cls):
        not_implemented()

    def permalink(self):
        not_implemented()


class Author(AtomBase):

    fields    = ['name', 'uri', 'email']
    __slots__ = fields

    @classmethod
    def by_name(cls, name):
        not_implemented()

    # TODO:
    #def permalink(self):
    #    not_implemented()


class Category(AtomBase):

    fields    = ['term', 'label']
    __slots__ = fields

    @classmethod
    def by_term(cls, term):
        not_implemented()

    # TODO:
    #def permalink(self):
    #    not_implemented()


# Plugin Code


def select_canonical_plugin(plugins, settings, config_var):
    provider = filter(lambda m: m.__module__ == settings[config_var], plugins)
    if len(provider) < 1:
        raise RuntimeError('No plugin for "%s" specified' % config_var)
    if len(provider) > 1:
        raise RuntimeError('Multiple plugins for "%s" available' % config_var)
    return provider[0]


class AtomProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'ATOM_PROVIDER')(settings)

    entry   = property(lambda self: self._provider.entry,
                       doc="The Atom Entry class")

    feed    = property(lambda self: self._provider.feed,
                       doc="The Atom Feed class")

    slug_re = property(lambda self: self._provider.slug_re,
                       doc="The Atom slug re")


class EntryPermalinkProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'ENTRY_PERMALINK')(settings)

    def authoritative(self, entry):
        return self._provider.authoritative(entry)


class FeedPermalinkProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'FEED_PERMALINK')(settings)

    def authoritative(self, feed):
        return self._provider.authoritative(feed)
