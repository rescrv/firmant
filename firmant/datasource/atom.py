import datetime
import json
import pytz

from firmant.plugins import PluginMount
from firmant.utils import not_implemented
from firmant.constants import isoformat


# Base classes for Atom data.


class Filter(object):

    __slots__ = ['to_json', 'from_json']

    def __init__(self, to_json=None, from_json=None):
        if not hasattr(self, 'to_json'):
            self.to_json   = to_json   or (lambda self: self)
        if not hasattr(self, 'from_json'):
            self.from_json = from_json or (lambda self: self)


class DatetimeFilter(Filter):

    def to_json(self, dt):
        if dt.tzinfo is None:
            return (dt.strftime(isoformat), None)
        else:
            utc_dt = dt.astimezone(pytz.UTC)
            return (utc_dt.strftime(isoformat), dt.tzinfo.zone)

    def from_json(self, dt):
        if dt[1] is None:
            return datetime.datetime.strptime(dt[0], isoformat)
        else:
            dt_obj = pytz.UTC.localize(datetime.datetime.strptime(dt[0],
                isoformat))
            tz_obj = pytz.timezone(dt[1])
            new_dt = dt_obj.astimezone(tz_obj)
            return tz_obj.normalize(new_dt)


class AtomObjectFilter(Filter):

    def __init__(self, cls):
        self.cls = cls

    def to_json(self, obj):
        return obj.to_json()

    def from_json(self, obj):
        return self.cls.from_json(obj)


class AtomObjectListFilter(Filter):

    def __init__(self, cls):
        self.cls = cls

    def to_json(self, obj_list):
        serialized_objs = map(lambda obj: obj.to_json(), obj_list)
        return json.dumps(serialized_objs)

    def from_json(self, obj_list):
        serialized_objs = json.loads(obj_list)
        return map(lambda s: self.cls.from_json(s), serialized_objs)


class AtomBase(object):

    filters = {}

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
    def json_filter(cls, field):
        return cls.filters.get(field, Filter())

    def to_json(self):
        data = {}
        for field in self.fields:
            if hasattr(self, field):
                filter = self.json_filter(field)
                value  = filter.to_json(getattr(self, field))
                data[field] = value
        return json.dumps(data)

    @classmethod
    def from_json(cls, string):
        data = json.loads(string)
        entry = cls()
        for field in cls.fields:
            if data.has_key(field):
                filter = cls.json_filter(field)
                value  = filter.from_json(data[field])
                setattr(entry, field, value)
        return entry


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


class Entry(AtomBase):

    # In case a subclass overloads __slots__ we can still compare two Entry
    # objects.
    fields    = ['slug', 'published', 'author', 'category', 'rights', 'updated',
                 'title', 'content', 'summary', 'tz']
    __slots__ = fields
    filters              = {}
    filters['published'] = DatetimeFilter()
    filters['updated']   = DatetimeFilter()
    filters['author']    = AtomObjectFilter(Author)
    filters['category']  = AtomObjectFilter(Category)

    @classmethod
    def for_feed(cls, feedslug):
        not_implemented()

    @classmethod
    def single(cls, slug, year, month, day):
        not_implemented()

    @classmethod
    def day(cls, year, month, day):
        not_implemented()

    @classmethod
    def month(cls, year, month):
        not_implemented()

    @classmethod
    def year(cls, year):
        not_implemented()

    @classmethod
    def recent(cls):
        not_implemented()

    @property
    def permalink(self):
        not_implemented()


class Feed(AtomBase):

    fields    = ['slug', 'title', 'rights', 'subtitle', 'updated']
    __slots__ = fields
    filters              = {}
    filters['updated']   = DatetimeFilter()

    @classmethod
    def by_slug(cls, slug):
        not_implemented()

    @classmethod
    def default(cls):
        not_implemented()

    @property
    def permalink(self):
        not_implemented()


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
