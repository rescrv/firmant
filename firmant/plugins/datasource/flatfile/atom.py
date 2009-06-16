# TODO:  This file is broken, primarily because permalinks are not added to
# Entry or Feed objects.  This may be fixed when this module gets more love.
# For now this module is going to be set aside now that the plugin interface
# behaves correctly.

import re
import os.path
import datetime
import pytz
import json

from firmant.datasource.atom import AtomProvider, \
                                    Entry, \
                                    Feed, \
                                    Author, \
                                    Category


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
date_re = re.compile('^\d{4}-\d{1,2}-\d{1,2}$')


class FlatfileAtomProvider(AtomProvider):

    __slots__ = ['feed', 'entry', 'author', 'category']
    slug_re = slug_re

    def __init__(provider_self, settings):

        class FlatFileEntry(Entry):

            provider = provider_self

            @classmethod
            def _load_one(cls, slug, date):
                """We assume that slug and date are validated elsehwere"""
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
                            (date, datetime.datetime.strptime \
                                (meta_data['time'], '%H%M%S').time()
                            )
                        )
                entry.author    = \
                        provider_self.author.by_name(meta_data['author'])
                entry.category  = \
                        provider_self.category.by_term(meta_data['category'])
                entry.rights    = rights_data
                entry.updated   = \
                        tz_obj.localize \
                        (datetime.datetime.strptime \
                            (meta_data['updated'], '%Y-%m-%d %H%M%S')
                        )
                entry.title     = meta_data['title']
                entry.content   = content_data
                entry.summary   = summary_data
                return entry

            @classmethod
            def _load_many(cls, entries):
                return filter(lambda e: e is not None,
                              map(lambda e: cls._load_one(*e), entries))

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

                entry = cls._load_one(slug, dt)
                return entry

            @classmethod
            def day(cls, year, month, day):
                try:
                    year  = int(year)
                    month = int(month)
                    day   = int(day)
                    dt = datetime.date(year, month, day)
                except ValueError:
                    raise
                return cls._day(dt)

            @classmethod
            def _day(cls, dt):
                entry_path = os.path.join(settings['FLATFILE_BASE'],
                                    'entries',
                                    '%02i' % dt.year,
                                    '%02i' % dt.month,
                                    '%02i' % dt.day)
                if not os.access(entry_path, os.R_OK):
                    return []

                slugs = os.listdir(entry_path)
                return cls._load_many(map(lambda e: (e, dt), slugs))

            @classmethod
            def month(cls, year, month):
                try:
                    year  = int(year)
                    month = int(month)
                    dt = datetime.date(year, month, 1)
                except ValueError:
                    raise
                return cls._month(dt)

            @classmethod
            def _month(cls, dt):
                entry_path = os.path.join(settings['FLATFILE_BASE'],
                                    'entries',
                                    '%02i' % dt.year,
                                    '%02i' % dt.month)
                if not os.access(entry_path, os.R_OK):
                    return []

                days = reversed(sorted(os.listdir(entry_path)))
                def invalid_day(day):
                    """Returns False if it cannot be converted to int or
                    produces an invalid date.  Returns the date object
                    otherwise."""
                    try:
                        day = int(day)
                        return datetime.date(dt.year, dt.month, day)
                    except ValueError:
                        return False
                clean_days = filter(lambda e: e, map(invalid_day, days))
                return reduce(lambda x, y: x + y,
                              map(cls._day, clean_days))

            @classmethod
            def year(cls, year):
                try:
                    year  = int(year)
                    dt = datetime.date(year, 1, 1)
                except ValueError:
                    raise
                return cls._year(dt)

            @classmethod
            def _year(cls, dt):
                entry_path = os.path.join(settings['FLATFILE_BASE'],
                                    'entries',
                                    '%02i' % dt.year)
                if not os.access(entry_path, os.R_OK):
                    return []
                months = reversed(sorted(os.listdir(entry_path)))
                def invalid_month(month):
                    """Returns False if it cannot be converted to int or
                    produces an invalid date.  Returns the date object
                    otherwise."""
                    try:
                        month = int(month)
                        return datetime.date(dt.year, month, 1)
                    except ValueError:
                        return False
                clean_months = filter(lambda e: e, map(invalid_month, months))
                return reduce(lambda x, y: x + y,
                              map(cls._month, clean_months))

            @classmethod
            def recent(cls):
                entry_path = os.path.join(settings['FLATFILE_BASE'],
                                        'entries')
                if not os.access(entry_path, os.R_OK):
                    return []
                years = reversed(sorted(os.listdir(entry_path)))
                def invalid_year(year):
                    """Returns False if it cannot be converted to int or
                    produces an invalid date.  Returns the date object
                    otherwise."""
                    try:
                        year = int(year)
                        return datetime.date(year, 1, 1)
                    except ValueError:
                        return False
                clean_years = filter(lambda e: e, map(invalid_year, years))
                return reduce(lambda x, y: x + y,
                              map(cls._year, clean_years))

        provider_self.entry = FlatFileEntry

        class FlatFileFeed(Feed):
            provider = provider_self

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
                path = os.path.join(settings['FLATFILE_BASE'], 'categories', term)
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
