import re
import os.path
import datetime
import pytz

from firmant.datasource.atom import AtomProvider, \
                                    Entry, \
                                    Feed, \
                                    Author, \
                                    Category, \
                                    EntryPermalinkProvider, \
                                    FeedPermalinkProvider
from firmant.datasource.atom import AtomFeedProvider
from firmant.datasource.atom import AtomEntryProvider
from firmant.datasource.atom import AtomAuthorProvider
from firmant.datasource.atom import AtomCategoryProvider
from firmant.datasource.atom import slug_re
from firmant.datasource import Storage
from firmant.utils import strptime
from firmant.utils import uniq_presorted
from firmant.utils import json


date_re = re.compile('^\d{4},\d{2},\d{2}$')


class AtomFlatfileCategoryProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def by_term(self, term):
        path = os.path.join(self.settings['FLATFILE_BASE'],
                            'categories',
                            term)
        if not os.access(path, os.R_OK):
            return None
        file = open(path)
        data = file.read().decode('utf-8')
        file.close()
        category       = Category()
        category.term  = term
        category.label = data
        return category

    def exists(self, term):
        path = os.path.join(self.settings['FLATFILE_BASE'],
                            'categories',
                            term)
        if not os.access(path, os.R_OK):
            return False
        return True

    def _save(self, obj):
        path = os.path.join(self.settings['FLATFILE_BASE'], 'categories',
                obj.term)
        if os.access(path, os.F_OK):
            raise Storage.UniqueViolationError('Category already exists')
        f = open(path, 'w')
        f.write(obj.label)
        f.flush()
        f.close()

    def _delete(self, obj):
        path = os.path.join(self.settings['FLATFILE_BASE'], 'categories',
                obj.term)
        if not os.access(path, os.F_OK):
            raise Storage.DoesNotExistError('Category does not exist')
        os.unlink(path)


class AtomFlatfileAuthorProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def by_name(self, name):
        path = os.path.join(self.settings['FLATFILE_BASE'], 'people', name)
        if not os.access(path, os.R_OK):
            return None
        file = open(path)
        data = file.read().decode('utf-8')
        file.close()
        jdata        = json.loads(data)
        author       = Author()
        author.name  = name
        author.uri   = jdata['uri']
        author.email = jdata['email']
        return author

    def exists(self, name):
        path = os.path.join(self.settings['FLATFILE_BASE'], 'people', name)
        if not os.access(path, os.R_OK):
            return False
        return True

    def _save(self, obj):
        path = os.path.join(self.settings['FLATFILE_BASE'], 'people', obj.name)
        if os.access(path, os.F_OK):
            raise Storage.UniqueViolationError('Author already exists')
        f = open(path, 'w')
        data = {}
        data['uri'] = obj.uri
        data['email'] = obj.email
        f.write(json.dumps(data))
        f.flush()
        f.close()

    def _delete(self, obj):
        path = os.path.join(self.settings['FLATFILE_BASE'], 'people', obj.name)
        if not os.access(path, os.F_OK):
            raise Storage.DoesNotExistError('Author does not exist')
        os.unlink(path)



class AtomFlatfileEntryProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings
        self.rc       = rc

    def _validate(self, slug, date):
        """Check all files exist.  We assume that slug and date are correct."""
        entry_path = os.path.join(self.settings['FLATFILE_BASE'],
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

    def _load_one(self, date, slug):
        """We assume that slug and date are validated elsehwere"""

        paths = self._validate(slug, date)

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

        content_data = content_file.read().decode('utf-8')
        meta_data    = meta_file.read().decode('utf-8')
        meta_data    = json.loads(meta_data)
        rights_data  = rights_file.read().decode('utf-8')
        summary_data = summary_file.read().decode('utf-8')

        content_file.close()
        meta_file   .close()
        rights_file .close()
        summary_file.close()

        entry           = Entry()
        entry.slug      = unicode(slug)
        entry.tz        = meta_data['timezone']
        tz_obj          = pytz.timezone(entry.tz)
        entry.published = \
                tz_obj.localize \
                (datetime.datetime.combine \
                    (date, strptime(meta_data['time'], '%H%M%S').time()
                    )
                )
        entry.author    = \
                self.rc().get(AtomAuthorProvider).\
                by_name(meta_data['author'])
        entry.category  = \
                self.rc().get(AtomCategoryProvider).\
                by_term(meta_data['category'])
        entry.rights    = rights_data
        entry.updated   = \
                tz_obj.localize \
                (strptime(meta_data['updated'], '%Y-%m-%d %H%M%S')                        )
        entry.title     = meta_data['title']
        entry.content   = content_data
        entry.summary   = summary_data
        entry.permalink = \
            self.rc().get(EntryPermalinkProvider).authoritative(entry.slug,
                    entry.published.date())
        return entry

    def _load_many(self, entries):
        return filter(lambda e: e is not None,
                      map(lambda e: self._load_one(*e), entries))

    def _paginate(self, entry_list, limit, offset):
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
                return (self._load_many(sliced_entries), length)
        return self._load_many(entry_list)

    def exists(self, slug, year, month, day):
        if slug_re.match(slug) == None:
            raise ValueError("Invalid Slug")
        try:
            year  = int(year)
            month = int(month)
            day   = int(day)
            dt    = datetime.date(year, month, day)
        except ValueError:
            raise
        valid_paths = self._validate(slug, dt)
        return valid_paths is not None

    def single(self, slug, year, month, day):
        if slug_re.match(slug) == None:
            raise ValueError("Invalid slug")

        try:
            year  = int(year)
            month = int(month)
            day   = int(day)
            dt = datetime.date(year, month, day)
        except ValueError:
            raise

        entry = self._load_one(dt, slug)
        return entry

    def day(self, year, month, day, limit=None, offset=None):
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
        entries_names = filter(entry_in_day, self.list())
        return self._paginate(entries_names, limit, offset)

    def month(self, year, month, limit=None, offset=None):
        try:
            year  = int(year)
            month = int(month)
            dt = datetime.date(year, month, 1)
        except ValueError:
            raise
        def entry_in_month(entry):
            return entry[0].year == dt.year and \
                   entry[0].month == dt.month
        entries_names = filter(entry_in_month, self.list())
        return self._paginate(entries_names, limit, offset)

    def year(self, year, limit=None, offset=None):
        try:
            year  = int(year)
            dt = datetime.date(year, 1, 1)
        except ValueError:
            raise
        def entry_in_year(entry):
            return entry[0].year == dt.year
        entries_names = filter(entry_in_year, self.list())
        return self._paginate(entries_names, limit, offset)

    def recent(self, limit=None, offset=None):
        entries_names = self.list()
        return self._paginate(entries_names, limit, offset)

    def for_feed(self, feedslug, limit=None, offset=None):
        if feedslug != '=default' and feedslug != '' and \
                slug_re.match(feedslug) == None:
            raise ValueError("Invalid slug")
        feed_path = os.path.join(self.settings['FLATFILE_BASE'],
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
        return self._paginate(parsed_entries, limit, offset)

    def list(self):
        entry_path = os.path.join(self.settings['FLATFILE_BASE'], 'entries')
        entry_path = os.path.abspath(entry_path)

        ret = []
        for dirpath, dirnames, filenames in os.walk(entry_path):
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
                if self._validate(tail, d) is not None:
                    ret.append((d, tail))
        return [x for x in reversed(sorted(ret))]

    def list_years(self):
        entries = self.list()
        def trunc_year(dt):
            return datetime.date(dt.year, 1, 1)
        years = map(lambda x: trunc_year(x[0]), entries)
        return uniq_presorted(years)

    def list_months(self):
        entries = self.list()
        def trunc_month(dt):
            return datetime.date(dt.year, dt.month, 1)
        months = map(lambda x: trunc_month(x[0]), entries)
        return uniq_presorted(months)

    def list_days(self):
        entries = self.list()
        days = map(lambda x: x[0], entries)
        return uniq_presorted(days)


class AtomFlatfileFeedProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings
        self.rc       = rc

    def by_slug(self, slug):
        if slug_re.match(slug) == None:
            raise ValueError("Invalid slug")
        return self._common(slug)

    def exists(self, slug):
        # TODO:  duplicates _common prefix and by_slug.  Fix it?
        if slug_re.match(slug) == None:
            raise ValueError("Invalid slug")
        feed_path = os.path.join(self.settings['FLATFILE_BASE'],
                                'feeds',
                                slug)

        rights_path = os.path.join(feed_path, 'rights')
        meta_path   = os.path.join(feed_path, 'meta')

        if not os.access(feed_path,   os.R_OK) or \
           not os.access(rights_path, os.R_OK) or \
           not os.access(meta_path,   os.R_OK):
            return False
        return True

    def _common(self, slug):
        feed_path = os.path.join(self.settings['FLATFILE_BASE'],
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

        rights_data = rights_file.read().decode('utf-8')
        meta_data   = json.loads(meta_file.read().decode('utf-8'))

        rights_file.close()
        meta_file  .close()

        feed          = Feed()
        feed.slug     = slug
        feed.title    = meta_data['title']
        feed.rights   = rights_data
        feed.subtitle = meta_data['subtitle']
        feed.entries  = self.rc().get(AtomEntryProvider).for_feed(slug)
        if slug == '=default':
            feed.permalink = \
            self.rc().get(FeedPermalinkProvider).authoritative('')
        else:
            feed.permalink = \
            self.rc().get(FeedPermalinkProvider).authoritative(feed.slug)
        if len(feed.entries) > 0:
            feed.updated  = feed.entries[0].updated
        else:
            feed.updated  = datetime.datetime(1900, 1, 1)
        return feed

    def default(self):
        feed = self._common('=default')
        feed.slug = ''
        return feed
