import datetime
import pytz
import os
import re

from firmant.utils import not_implemented


comment_re = r'(?P<year>\d{4}),(?P<month>\d{2}),(?P<day>\d{2}),(?P<slug>.+)' +\
    r',(?P<created>[1-9][0-9]*),(?P<id>[0-9a-f]{40})'
comment_re = re.compile(comment_re)


class FlatfileCommentProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def for_entry(self, status, slug, year, month, day):
        not_implemented()
