import datetime
import pytz
import os
import re

from firmant.utils import not_implemented
from firmant.datasource.comments import Comment


comment_re = r'(?P<year>\d{4}),(?P<month>\d{2}),(?P<day>\d{2}),(?P<slug>.+)' +\
    r',(?P<created>[1-9][0-9]*),(?P<id>[0-9a-f]{40})'
comment_re = re.compile(comment_re)


class FlatfileCommentProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def for_entry(self, status, slug, year, month, day):
        not_implemented()

    def _load_one(self, status, entry_pkey, created, id):
        comment_dt       = entry_pkey[0].strftime('%Y,%m,%d')
        comment_filename = '%s,%s,%i,%s' % \
                (comment_dt, entry_pkey[1], created, id)
        comment_path     = os.path.join(self.settings['FLATFILE_BASE'],
                                    'comments',
                                    status,
                                    comment_filename)

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

        created_dt      = datetime.datetime.fromtimestamp(created)
        comment.created = pytz.utc.localize(created_dt)

        return comment
