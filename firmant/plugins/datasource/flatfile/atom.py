# TODO:  This file is broken, primarily because permalinks are not added to
# Entry or Feed objects.  This may be fixed when this module gets more love.
# For now this module is going to be set aside now that the plugin interface
# behaves correctly.

import re
import os.path
import datetime
import pytz

from firmant.datasource.atom import AtomProvider


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
date_re = re.compile('^\d{4}-\d{1,2}-\d{1,2}$')


class FlatfileAtomProvider(AtomProvider):

    __slots__ = ['feed', 'entry']
    slug_re = slug_re

    def __init__(provider_self, settings):

        class Entry(object):

            provider = provider_self
            attributes = ['slug', 'published', 'author_name',
                          'author_uri', 'author_email', 'category_term',
                          'category_label', 'rights', 'updated', 'title',
                          'content', 'summary', 'tz']

            @classmethod
            def for_feed(cls, feedname):
                pass

            @classmethod
            def single(cls, slug, date):
                pass

            @classmethod
            def day(cls, year, month, day):
                pass

            @classmethod
            def month(cls, year, month):
                pass

            @classmethod
            def year(cls, year):
                pass

            @classmethod
            def recent(cls, upper_bound=datetime.datetime.max):
                pass
        provider_self.entry = Entry

        class Feed(object):

            provider = provider_self
            attributes = ['slug', 'title', 'rights', 'subtitle', 'updated']

            @classmethod
            def by_name(cls, name):
                pass
        provider_self.feed = Feed
