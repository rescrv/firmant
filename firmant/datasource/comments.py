import datetime
import pytz

from firmant.plugins import SingleProviderPlugin


class Comment(object):

    fields    = ['name', 'email', 'url', 'ip', 'useragent', 'created',
            'content', 'status', 'entry_pkey']

    __slots__ = fields

    def __eq__(self, other):
        for field in self.fields:
            if hasattr(self, field) \
               and hasattr(other, field) \
               and getattr(self, field) != getattr(other, field):
                return False
            if hasattr(self, field) \
               and not hasattr(other, field):
                return False
            if not hasattr(self, field) \
               and hasattr(other, field):
                return False
        return True


class CommentProvider(SingleProviderPlugin):

    provider_setting = 'COMMENT_PROVIDER'

    def for_entry(self, status, slug, year, month, day):
        return self._provider.for_entry(status, slug, year, month, day)

    class DoesNotExistError(Exception): pass
    class StorageError(Exception): pass
    class UniqueViolationError(Exception): pass
