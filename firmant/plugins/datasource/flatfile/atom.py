import re
import os.path
import datetime
import pytz
try:
    import json
except ImportError:
    import simplejson as json

from firmant.datasource.atom import AtomProvider, \
                                    Entry, \
                                    Feed, \
                                    Author, \
                                    Category, \
                                    EntryPermalinkProvider, \
                                    FeedPermalinkProvider
from firmant.utils import strptime
from firmant.utils import uniq_presorted


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
date_re = re.compile('^\d{4},\d{2},\d{2}$')


class FlatfileAtomProvider(AtomProvider):

    __slots__ = ['feed', 'entry', 'author', 'category']
    slug_re = slug_re

    def __init__(provider_self, settings):

        class FlatFileEntry(Entry):

            provider = provider_self

            @classmethod
            def _validate(cls, slug, date):
                """Check all files exist.  We assume that slug and date are correct."""
                entry_path = os.path.join(settings['FLATFILE_BASE'],
                                    'entries',
                                    '%02i' % date.year,
                                    '%02i' % date.month,
                                    '%02i' % date.day,
                                    slug)

                content_path = os.path.join(entry_path, 'content')
                meta_path    = os.path.join(entry_path, 'meta')
                rights_path  = os.path.join(entry_path, 'rights')
                summary_path = os.path.join(entry_path, 'summary')

                if not os.access(content_path, os.R_OK) or \
                   not os.access(meta_path,    os.R_OK) or \
                   not os.access(rights_path,  os.R_OK) or \
                   not os.access(summary_path, os.R_OK):
                    return None

                return (content_path, meta_path, rights_path, summary_path)

            @classmethod
            def _load_one(cls, date, slug):
                """We assume that slug and date are validated elsehwere"""

                paths = cls._validate(slug, date)

                if paths is None:
                    return None

                content_path = paths[0]
                meta_path    = paths[1]
                rights_path  = paths[2]
                summary_path = paths[3]

                content_file = open(content_path)
                meta_file    = open(meta_path)
                rights_file  = open(rights_path)
                summary_file = open(summary_path)

                content_data = content_file.read()
                meta_data    = meta_file.read()
                meta_data    = json.loads(meta_data)
                rights_data  = rights_file.read()
                summary_data = summary_file.read()

                content_file.close()
                meta_file   .close()
                rights_file .close()
                summary_file.close()

                entry = cls()
                entry.slug      = slug
                entry.tz        = meta_data['timezone']
                tz_obj          = pytz.timezone(entry.tz)
                entry.published = \
                        tz_obj.localize \
                        (datetime.datetime.combine \
                            (date, strptime(meta_data['time'], '%H%M%S').time()
                            )
                        )
                entry.author    = \
                        provider_self.author.by_name(meta_data['author'])
                entry.category  = \
                        provider_self.category.by_term(meta_data['category'])
                entry.rights    = rights_data
                entry.updated   = \
                        tz_obj.localize \
                        (strptime(meta_data['updated'], '%Y-%m-%d %H%M%S')                        )
                entry.title     = meta_data['title']
                entry.content   = content_data
                entry.summary   = summary_data
                return entry

            @classmethod
            def _load_many(cls, entries):
                return filter(lambda e: e is not None,
                              map(lambda e: cls._load_one(*e), entries))

            @classmethod
            def _paginate(cls, entry_list, limit, offset):
                if limit is not None or offset is not None:
                    if limit is None:
                        limit = 10
                    if offset is None:
                        offset = 0
                    if limit < 0:
                        raise ValueError("Cannot have negative limit value.")
                    if offset < 0:
                        raise ValueError("Cannot have negative offset value.")
                    if offset >= len(entry_list):
                        return (None, 0)
                    else:
                        length = len(entry_list) - limit - offset
                        length = max(length, 0)
                        sliced_entries = entry_list[offset:limit + offset]
                        return (cls._load_many(sliced_entries), length)
                return cls._load_many(entry_list)

            @classmethod
            def single(cls, slug, year, month, day):
                if provider_self.slug_re.match(slug) == None:
                    raise ValueError("Invalid slug")

                try:
                    year  = int(year)
                    month = int(month)
                    day   = int(day)
                    dt = datetime.date(year, month, day)
                except ValueError:
                    raise

                entry = cls._load_one(dt, slug)
                return entry

            @classmethod
            def day(cls, year, month, day, limit=None, offset=None):
                try:
                    year  = int(year)
                    month = int(month)
                    day   = int(day)
                    dt = datetime.date(year, month, day)
                except ValueError:
                    raise
                def entry_in_day(entry):
                    return entry[0].year == dt.year and \
                           entry[0].month == dt.month and \
                           entry[0].day == dt.day
                entries_names = filter(entry_in_day, cls.list())
                return cls._paginate(entries_names, limit, offset)

            @classmethod
            def month(cls, year, month, limit=None, offset=None):
                try:
                    year  = int(year)
                    month = int(month)
                    dt = datetime.date(year, month, 1)
                except ValueError:
                    raise
                def entry_in_month(entry):
                    return entry[0].year == dt.year and \
                           entry[0].month == dt.month
                entries_names = filter(entry_in_month, cls.list())
                return cls._paginate(entries_names, limit, offset)

            @classmethod
            def year(cls, year, limit=None, offset=None):
                try:
                    year  = int(year)
                    dt = datetime.date(year, 1, 1)
                except ValueError:
                    raise
                def entry_in_year(entry):
                    return entry[0].year == dt.year
                entries_names = filter(entry_in_year, cls.list())
                return cls._paginate(entries_names, limit, offset)

            @classmethod
            def recent(cls):
                entries_names = cls.list()
                return cls._load_many(entries_names)

            @classmethod
            def for_feed(cls, feedslug, limit=None, offset=None):
                if feedslug != '' and \
                   provider_self.slug_re.match(feedslug) == None:
                    raise ValueError("Invalid slug")
                feed_path = os.path.join(settings['FLATFILE_BASE'],
                                        'feeds',
                                        feedslug)
                if not os.access(feed_path, os.R_OK):
                    return None
                entries = reversed(sorted(os.listdir(feed_path)))
                def is_entry(entry):
                    return date_re.match(entry[:10]) is not None and \
                           slug_re.match(entry[11:]) is not None
                cleaned_entries = filter(is_entry, entries)
                def parse(entry):
                    dt = strptime(entry[:10], '%Y,%m,%d').date()
                    slug = entry[11:]
                    return (dt, slug)
                parsed_entries = map(parse, cleaned_entries)
                return cls._paginate(parsed_entries, limit, offset)

            @property
            def permalink(self):
                return provider_self.entry_permalink(self)

            @classmethod
            def list(cls):
                entry_path = os.path.join(settings['FLATFILE_BASE'], 'entries')
                entry_path = os.path.abspath(entry_path)

                ret = []
                for dirpath, dirnames, filenames in os.walk(entry_path):
                    if not dirpath.startswith(entry_path):
                        raise ValueError('dirpath outside entry_path')
                    path = dirpath[len(entry_path):]
                    head, tail = os.path.split(path)
                    match_tail = slug_re.match(tail)
                    match_head = re.match(r'/(\d{4})/(\d{2})/(\d{2})', head)
                    if match_head is not None and \
                       match_tail is not None:
                        groups = match_head.groups()
                        d = datetime.date(int(groups[0]),
                                          int(groups[1]),
                                          int(groups[2]))
                        if cls._validate(tail, d) is not None:
                            ret.append((d, tail))
                return [x for x in reversed(sorted(ret))]

            @classmethod
            def list_years(cls):
                entries = cls.list()
                def trunc_year(dt):
                    return datetime.date(dt.year, 1, 1)
                years = map(lambda x: trunc_year(x[0]), entries)
                return uniq_presorted(years)

            @classmethod
            def list_months(cls):
                entries = cls.list()
                def trunc_month(dt):
                    return datetime.date(dt.year, dt.month, 1)
                months = map(lambda x: trunc_month(x[0]), entries)
                return uniq_presorted(months)

            @classmethod
            def list_days(cls):
                entries = cls.list()
                days = map(lambda x: x[0], entries)
                return uniq_presorted(days)

        provider_self.entry = FlatFileEntry

        class FlatFileFeed(Feed):

            provider = provider_self

            @classmethod
            def by_slug(cls, slug):
                if slug != '' and provider_self.slug_re.match(slug) == None:
                    raise ValueError("Invalid slug")

                feed_path = os.path.join(settings['FLATFILE_BASE'],
                                        'feeds',
                                        slug)

                rights_path = os.path.join(feed_path, 'rights')
                meta_path   = os.path.join(feed_path, 'meta')

                if not os.access(feed_path,   os.R_OK) or \
                   not os.access(rights_path, os.R_OK) or \
                   not os.access(meta_path,   os.R_OK):
                    return None

                rights_file = open(rights_path)
                meta_file   = open(meta_path)

                rights_data = rights_file.read()
                meta_data   = json.loads(meta_file.read())

                rights_file.close()
                meta_file  .close()

                feed = cls()
                feed.slug     = slug
                feed.title    = meta_data['title']
                feed.rights   = rights_data
                feed.subtitle = meta_data['subtitle']
                feed.entries  = provider_self.entry.for_feed(slug)
                if len(feed.entries) > 0:
                    feed.updated  = feed.entries[0].updated
                else:
                    feed.updated  = datetime.datetime.min
                return feed

            @classmethod
            def default(cls):
                feed = cls()
                feed.slug     = ''
                feed.title    = settings['ATOM_DEFAULT_TITLE']
                feed.rights   = settings['ATOM_DEFAULT_RIGHTS']
                feed.subtitle = settings['ATOM_DEFAULT_SUBTITLE']
                feed.entries  = provider_self.entry.for_feed('')
                if len(feed.entries) > 0:
                    feed.updated  = feed.entries[0].updated
                else:
                    feed.updated  = datetime.datetime.min
                return feed

            @property
            def permalink(self):
                return provider_self.feed_permalink(self)

        provider_self.feed = FlatFileFeed

        class FlatFileAuthor(Author):

            provider = provider_self

            @classmethod
            def by_name(cls, name):
                path = os.path.join(settings['FLATFILE_BASE'], 'people', name)
                if not os.access(path, os.R_OK):
                    return None
                file = open(path)
                data = file.read()
                file.close()
                author = cls.from_json(data)
                author.name = name
                return author

        provider_self.author = FlatFileAuthor

        class FlatFileCategory(Category):

            provider = provider_self

            @classmethod
            def by_term(cls, term):
                path = os.path.join(settings['FLATFILE_BASE'],
                                    'categories',
                                    term)
                if not os.access(path, os.R_OK):
                    return None
                file = open(path)
                data = file.read()
                file.close()
                category       = cls()
                category.term  = term
                category.label = data
                return category

        provider_self.category = FlatFileCategory

        provider_self.entry_permalink = \
                EntryPermalinkProvider(settings).authoritative

        provider_self.feed_permalink = \
                FeedPermalinkProvider(settings).authoritative
