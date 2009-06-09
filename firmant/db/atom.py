import re
import psycopg2
import os.path
import datetime
import pytz

from firmant.configuration import settings
from firmant.db.relations import Relation
from firmant.backend.atom import AtomProvider


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
date_re = re.compile('^\d{4}-\d{1,2}-\d{1,2}$')


class AtomDB(object):

    def __init__(self, settings):
        # We must initialize settings before ro_connection.
        self.settings = settings
        self.ro_connection = self.connection(readonly=True)
        self.ro_connection.set_isolation_level(0)

    def connection(self, readonly=True):
        if readonly:
            return psycopg2.connect(self.settings['ATOM_DB_CONNECT'])
        else:
            return psycopg2.connect(self.settings['ATOM_DB_CONNECT_WRITE'])

    def readonly_cursor(self):
        cur = self.ro_connection.cursor()
        cur.execute('SET search_path = atom;')
        return cur


class Entry(Relation):

    attributes = ['slug', 'published', 'author_name',
                  'author_uri', 'author_email', 'category_term',
                  'category_label', 'rights', 'updated', 'title', 'content',
                  'summary', 'tz']

    @classmethod
    def _select(cls, cursor, fields):
        entries = super(Entry, cls)._select(cursor, fields)
        for entry in entries:
            tz = pytz.timezone(entry.tz)
            entry.published = tz.localize(entry.published)
            entry.updated = tz.localize(entry.updated)
        return entries

    @classmethod
    def for_feed(cls, feedname):
        sql = """SELECT ep.slug, ep.published, ep.name, ep.uri, ep.email,
                        ep.term, ep.label, ep.rights, ep.updated, ep.title,
                        ep.content, ep.summary, ep.tz
                 FROM entries_published ep, feeds f, _feeds_entries_join fej
                 WHERE f.slug = fej.feeds_slug AND
                       fej.entries_slug = ep.slug AND
                       fej.entries_published_date = ep.published_date AND
                       f.slug = %(slug)s;"""
        cur = AtomDB(settings).readonly_cursor()
        params = {'slug': feedname}
        cur.execute(sql, params)
        results = cls._select(cur, cls.attributes)
        cur.close()
        return results

    @classmethod
    def single(cls, slug, date):
        if slug_re.match(slug) == None:
            raise ValueError('Invalid slug')
        try:
            datestr = date.strftime('%Y-%m-%d')
        except AttributeError, e:
            raise ValueError('date should provide strftime')

        cur = AtomDB(settings).readonly_cursor()
        sql = """SELECT slug, published, name, uri, email, term, label, rights,
                        updated, title, content, summary, tz
                 FROM entries_published
                 WHERE slug=%(slug)s AND
                       published_date=%(date)s;"""
        params = {'slug': slug, 'date': datestr}
        cur.execute(sql, params)
        results = cls._select(cur, cls.attributes)
        cur.close()
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]

    @classmethod
    def day(cls, year, month, day):
        return cls._date_trunc('day', year, month, day)

    @classmethod
    def month(cls, year, month):
        return cls._date_trunc('month', year, month)

    @classmethod
    def year(cls, year):
        return cls._date_trunc('year', year)

    @classmethod
    def _date_trunc(cls, trunc='day', year=1, month=1, day=1):
        # If this raises an error, let it rise up.
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            raise
        if trunc not in set(['day', 'month', 'year']):
            raise ValueError('Must truncate to the day, month, or year')
        cur = AtomDB(settings).readonly_cursor()
        sql = """SELECT slug, published, name, uri, email, term, label, rights,
                        updated, title, content, summary, tz
                 FROM entries_published
                 WHERE date_trunc(%(trunc)s, published_date)=%(date)s;"""
        params = {'date': dt.strftime('%Y-%m-%d'), 'trunc': trunc}
        cur.execute(sql, params)
        results = cls._select(cur, cls.attributes)
        cur.close()
        return results

    @classmethod
    def recent(cls, upper_bound=datetime.datetime.max):
        # If this raises an error, let it rise up.
        cur = AtomDB(settings).readonly_cursor()
        sql = """SELECT slug, published, name, uri, email, term, label, rights,
                        updated, title, content, summary, tz
                 FROM entries_published
                 WHERE published < %(upper_bound)s;"""
        cur.execute(sql, {'upper_bound': upper_bound})
        results = cls._select(cur, cls.attributes)
        cur.close()
        return results


class Feed(Relation):

    attributes = ['slug', 'title', 'rights', 'subtitle', 'updated']

    sql = """
        SELECT f.slug, f.title, f.rights, f.subtitle, MAX(er.updated)
        FROM feeds f, _feeds_entries_join f_e, entries e, entry_revisions er
        WHERE f.slug = f_e.feeds_slug AND
            f_e.entries_slug = e.slug AND
            f_e.entries_published_date = e.published_date AND
            e.slug = er.slug AND
            e.published_date = er.published_date AND
            f.slug = %(slug)s
        GROUP BY f.slug, f.title, f.rights, f.subtitle;
        """

    @classmethod
    def by_name(cls, name):
        # If this raises an error, let it rise up.
        cur = AtomDB(settings).readonly_cursor()
        cur.execute(Feed.sql, {'slug': name})
        results = cls._select(cur, cls.attributes)
        cur.close()
        if len(results) == 0:
            return None
        feed = results[0]
        feed.entries = Entry.for_feed(name)
        return feed


class PostgresAtomProvider(AtomProvider):
    entry = Entry
    feed = Feed
    slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
