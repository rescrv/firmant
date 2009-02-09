import re
import psycopg2
import os.path

from firmant.configuration import settings
from firmant.db.relations import Relation
from firmant.db.relations import schema
from firmant.db.relations import DB


slug_re = re.compile('^[-\\_a-zA-Z0-9]{1,96}$')
date_re = re.compile('^\d{4}-\d{1,2}-\d{1,2}$')


class AtomDB(object):

    @staticmethod
    def connection(readonly=True):
        if readonly:
            return psycopg2.connect(settings['ATOM_DB_CONNECT'])
        else:
            return psycopg2.connect(settings['ATOM_DB_CONNECT_WRITE'])

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

    attributes = ['slug', 'published_date', 'published_time', 'author_name',
                  'author_uri', 'author_email', 'category_term',
                  'category_label', 'rights', 'updated', 'title', 'content',
                  'summary',]

    def single(self, slug, date):
        sql = """
        SELECT e.slug, e.published_date, e.published_time, p.name, p.uri,
               p.email, ca.term, ca.label, e.rights, er.updated, er.title,
               co.content, co.summary
        FROM entries e, people p, categories ca, entry_revisions er, content co
        WHERE e.author = p.name AND
              e.category = ca.term AND
              er.slug = e.slug AND
              er.published_date = e.published_date AND
              er.content = co.id
        ORDER BY er.updated DESC
        LIMIT 1;
        """
        if slug_re.match(slug) == None:
            raise ValueError('Invalid slug')
        try:
            if date_re.match(date) != None:
                datestr = date
            else:
                raise ValueError('Invalid date')
        except TypeError, e:
            try:
                datestr = date.strftime('%Y-%m-%d')
            except AttributeError, e:
                raise ValueError('Invalid date')

        conn = AtomDB.connection(readonly=True)
        cur = conn.cursor()

        try:
            cur.execute('SET search_path = atom;')
            cur.execute(sql)
        except psycopg2.DataError, e:
            cur.close()
            conn.close()
            raise ValueError('Invalid date')

        results = self._select(cur, self.attributes)
        cur.close()
        conn.close()
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        else:
            raise ValueError("A single select returned multiple")
