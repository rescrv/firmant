# TODO:  This file is broken, primarily because permalinks are not added to
# Entry or Feed objects.  This may be fixed when this module gets more love.
# For now this module is going to be set aside now that the plugin interface
# behaves correctly.

import re
import os.path
import datetime
import pytz

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

        provider_self.category = FlatFileCategory
