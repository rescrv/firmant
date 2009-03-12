import re
import psycopg2
import os.path
import datetime

from firmant.configuration import settings
from firmant.db.relations import Relation
from firmant.db.relations import schema
from firmant.db.relations import DB


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
date_re = re.compile('^\d{4}-\d{1,2}-\d{1,2}$')


class AtomDB(object):

    ro_connection = None

    @staticmethod
    def connection(readonly=True):
        if readonly:
            return psycopg2.connect(settings['ATOM_DB_CONNECT'])
        else:
            return psycopg2.connect(settings['ATOM_DB_CONNECT_WRITE'])

    @staticmethod
    def readonly_cursor():
        if AtomDB.ro_connection == None:
            AtomDB.ro_connection = AtomDB.connection(readonly=True)
            AtomDB.ro_connection.set_isolation_level(0)
        return AtomDB.ro_connection.cursor()

    @staticmethod
    def reset():
        AtomDB._drop()
        AtomDB._setup()

    @staticmethod
    def _drop():
        conn = DB.connection()
        cur = conn.cursor()
        cur.execute('DROP SCHEMA IF EXISTS atom CASCADE;')
        cur.close()
        conn.commit()
        conn.close()

    @staticmethod
    def _setup():
        atom = schema('atom')
        conn = DB.connection()
        cur = conn.cursor()
        cur.execute(atom)
        cur.close()
        conn.commit()
        conn.close()


class Entry(Relation):

    attributes = ['slug', 'published', 'author_name',
                  'author_uri', 'author_email', 'category_term',
                  'category_label', 'rights', 'updated', 'title', 'content',
                  'summary']

    sql = """
        SELECT e.slug, (e.published_date + e.published_time)::TIMESTAMP WITH
            TIME ZONE AT TIME ZONE 'GMT', p.name, p.uri, p.email, ca.term,
            ca.label, e.rights, er.updated AT TIME ZONE 'GMT', er.title,
            co.content, co.summary
        FROM entries e, people p, categories ca, entry_revisions er, content co
        WHERE e.author = p.name AND
            e.category = ca.term AND
            er.slug = e.slug AND
            er.published_date = e.published_date AND
            er.content = co.id AND
            %(additional)s AND
            (er.slug, er.published_date, er.updated) IN
                (SELECT er2.slug,
                    er2.published_date,
                    MAX(er2.updated)
                FROM entry_revisions er2
                GROUP BY er2.slug, er2.published_date)
        ORDER BY e.published_date DESC, e.published_time DESC, e.slug ASC;
        """

    @classmethod
    def for_feed(cls, feedname):
        # Monkey Patch SQL to find for feeds.  Perhaps I will rewrite to be
        # cleaner.
        i = Entry.sql.find('WHERE')
        newsql = Entry.sql[:i]
        newsql += ''', feeds f, _feeds_entries_join fej '''
        newsql += Entry.sql[i:]
        cur = AtomDB.readonly_cursor()
        params = {'additional':
                """f.slug = fej.feeds_slug AND
                fej.entries_slug = e.slug AND
                fej.entries_published_date = e.published_date AND
                f.slug = %(slug)s
                """}
        newsql = newsql % params
        params = {'slug': feedname}
        cur.execute('SET search_path = atom;')
        cur.execute(newsql, params)
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

        cur = AtomDB.readonly_cursor()
        params = {'additional': """e.slug=%(slug)s
                                   AND e.published_date=%(date)s"""}
        singlesql = Entry.sql % params
        params = {'slug': slug, 'date': datestr}
        cur.execute('SET search_path = atom;')
        cur.execute(singlesql, params)
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
        cur = AtomDB.readonly_cursor()
        params = {'additional':
                """date_trunc(%(trunc)s, e.published_date)=%(date)s"""}
        daysql = Entry.sql % params
        params = {'date': dt.strftime('%Y-%m-%d'), 'trunc': trunc}
        cur.execute('SET search_path = atom;')
        cur.execute(daysql, params)
        results = cls._select(cur, cls.attributes)
        cur.close()
        return results

    @classmethod
    def recent(cls):
        # If this raises an error, let it rise up.
        cur = AtomDB.readonly_cursor()
        params = {'additional': '1=1'}
        sql = Entry.sql % params
        cur.execute('SET search_path = atom;')
        cur.execute(sql)
        results = cls._select(cur, cls.attributes)
        cur.close()
        return results
