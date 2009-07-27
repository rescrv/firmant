import datetime
import pytz
import os
import re
import time
import calendar

from firmant.utils import not_implemented
from firmant.datasource.comments import Comment


comment_re = r'(?P<year>\d{4}),(?P<month>\d{2}),(?P<day>\d{2}),(?P<slug>.+)' +\
    r',(?P<created>[1-9][0-9]*),(?P<id>[0-9a-f]{40})'
comment_re = re.compile(comment_re)


class FlatfileCommentProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def for_entry(self, status, slug, year, month, day):
        try:
            dt = datetime.date(int(year), int(month), int(day))
        except ValueError:
            raise
        if status == '':
            raise ValueError("Status is ''")
        comments_list = self._list()
        def status_filter(comment):
            if status is None:
                return True
            else:
                return comment[0] == status
        comments_list = filter(status_filter, comments_list)
        def entry_filter(comment):
            return comment[1] == (dt, slug)
        comments_list = filter(entry_filter, comments_list)
        return map(lambda x: self._load_one(*x), comments_list)

    def __file(self, status, entry_pkey, created, id):
        comment_dt       = entry_pkey[0].strftime('%Y,%m,%d')
        comment_filename = '%s,%s,%i,%s' % \
                (comment_dt, entry_pkey[1], created, id)
        comment_path     = os.path.join(self.settings['FLATFILE_BASE'],
                                    'comments',
                                    status,
                                    comment_filename)
        return comment_path

    def _list(self):
        '''Returns a list of comments.  It's a tuple:
        (status, entry_pkey (date, slug), time_published, comment_id).
        This tuple is unique to this implementation.'''
        comment_base = os.path.join(self.settings['FLATFILE_BASE'], 'comments')
        ret = []
        statuses = os.listdir(comment_base)
        for status in statuses:
            comments = os.listdir(os.path.join(comment_base, status))
            for comment in comments:
                match = comment_re.match(comment)
                if match != None:
                    groups = match.groupdict()
                    try:
                        dt = datetime.date(int(groups['year']),
                                           int(groups['month']),
                                           int(groups['day']))
                        slug = groups['slug']
                        created = int(groups['created'])
                        id = groups['id']
                        ret.append((status, (dt, slug), created, id))
                    except ValueError:
                        pass
        def sort_results(a, b):
            if a[1] == b[1]:
                if a[2] < b[2]:
                    return -1
                elif a[2] > b[2]:
                    return 1
                else:
                    return 0
            elif a[1] < b[1]:
                return -1
            elif a[1] > b[1]:
                return 1
        ret.sort(sort_results)
        return ret

    def _load_one(self, status, entry_pkey, created, id):
        comment_path = self.__file(status, entry_pkey, created, id)

        if not os.access(comment_path, os.R_OK):
            return None

        f = open(comment_path)
        d = f.read()
        f.close()

        headers, content = d.split('\n\n', 1)

        comment = Comment()
        for header in headers.split('\n'):
            if header.startswith('Name:\t'):
                comment.name = header[6:]
            elif header.startswith('Email:\t'):
                comment.email = header[7:]
            elif header.startswith('URL:\t'):
                comment.url = header[5:]
            elif header.startswith('Host:\t'):
                comment.ip = header[6:]
            elif header.startswith('Agent:\t'):
                comment.useragent = header[7:]

        if content.endswith('\n'):
            content = content[:-1]
        comment.content = content

        comment.status = status
        comment.entry_pkey = entry_pkey

        comment.created = datetime.datetime(*time.gmtime(created)[:6],
                tzinfo=pytz.utc)

        return comment
