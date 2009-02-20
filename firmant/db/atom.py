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

    attributes = ['slug', 'published', 'author_name',
                  'author_uri', 'author_email', 'category_term',
                  'category_label', 'rights', 'updated', 'title', 'content',
                  'summary']

    @classmethod
    def single(cls, slug, date):
        if slug_re.match(slug) == None:
            raise ValueError('Invalid slug')
        try:
            datestr = date.strftime('%Y-%m-%d')
        except AttributeError, e:
            raise ValueError('date should provide strftime')

        conn = AtomDB.connection(readonly=True)
        cur = conn.cursor()
        cur = cls._posts_in_range(cur, slug, datestr, datestr)
        results = cls._select(cur, cls.attributes)
        cur.close()
        conn.close()
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]

    @classmethod
    def _posts_in_range(cls, cur, slug, min, max):
        additional_compare = {'min_pub_date': '%(min_pub_date)s',
                              'max_pub_date': '%(max_pub_date)s',
                              'slugselect': ''}
        params = {'min_pub_date': min, 'max_pub_date': max}
        if slug != None:
            additional_compare['slugselect'] = 'e.slug = %(slug)s'
            params['slug'] = slug
        sql = """
        SELECT e.slug, (e.published_date + e.published_time)::TIMESTAMP WITH
               TIME ZONE AT TIME ZONE 'GMT', p.name, p.uri, p.email,
               ca.term, ca.label, e.rights, er.updated AT TIME ZONE 'GMT',
               er.title, co.content, co.summary
        FROM entries e, people p, categories ca, entry_revisions er, content co
        WHERE e.author = p.name AND
              e.category = ca.term AND
              e.published_date <= %(max_pub_date)s AND
              e.published_date >= %(min_pub_date)s AND
              er.slug = e.slug AND
              er.published_date = e.published_date AND
              er.content = co.id AND
              %(slugselect)s
        ORDER BY er.updated DESC
        LIMIT 1;
        """ % additional_compare
        cur.execute('SET search_path = atom;')
        cur.execute(sql, params)

        return cur
