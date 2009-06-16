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
            def single(cls, slug, date):
                if provider_self.slug_re.match(slug) == None:
                    raise ValueError("Invalid slug")

                if not hasattr(date, 'year') or \
                   not hasattr(date, 'month') or \
                   not hasattr(date, 'day'):
                    raise ValueError("Invalid datetime")

                entry = cls._load_one(slug, date)
                return entry

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
