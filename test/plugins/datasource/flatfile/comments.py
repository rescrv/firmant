import unittest
import datetime
import pytz
import shutil

from firmant.plugins.datasource.flatfile.comments import FlatfileCommentProvider

from test.datasource.comments import TestCommentProvider as BaseTestCommentProvider


class TestCommentProvider(BaseTestCommentProvider):

    def setUp(self):
        settings = {'FLATFILE_BASE': 'checkout/'}
        self.provider = FlatfileCommentProvider(None, settings)


from test import add_test
suite = unittest.TestSuite()
add_test(suite, TestCommentProvider)
