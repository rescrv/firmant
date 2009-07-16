import datetime
try:
    import json
except ImportError:
    import simplejson as json
import pytz

from firmant.plugins import PluginMount
from firmant.plugins import SingleProviderPlugin
from firmant.utils import not_implemented
from firmant.constants import isoformat
from firmant.utils import xml, \
                          RFC3339, \
                          strptime


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
            return strptime(dt[0], isoformat)
        else:
            dt_obj = pytz.UTC.localize(strptime(dt[0], isoformat))
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
    filters              = {}
    filters['published'] = DatetimeFilter()
    filters['updated']   = DatetimeFilter()
    filters['author']    = AtomObjectFilter(Author)
    filters['category']  = AtomObjectFilter(Category)

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
    filters              = {}
    filters['updated']   = DatetimeFilter()

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


def select_canonical_plugin(plugins, settings, config_var):
    provider = filter(lambda m: m.__module__ == settings[config_var], plugins)
    if len(provider) < 1:
        raise RuntimeError('No plugin for "%s" specified' % config_var)
    if len(provider) > 1:
        raise RuntimeError('Multiple plugins for "%s" available' % config_var)
    return provider[0]


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

    def authoritative(self, entry):
        return self._provider.authoritative(entry)


class FeedPermalinkProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, rc, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'FEED_PERMALINK')(rc, settings)

    def authoritative(self, feed):
        return self._provider.authoritative(feed)
