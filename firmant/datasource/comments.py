import datetime
import pytz
import urlparse

from firmant.plugins import SingleProviderPlugin
from firmant.plugins import MultiProviderPlugin
from firmant.utils import email_re


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

    def save(self, comment):
        return self._provider.save(comment)

    def delete(self, comment):
        return self._provider.delete(comment)


class CommentValidator(MultiProviderPlugin):

    providers_setting = 'COMMENT_VALIDATORS'

    def is_valid(self, comment):
        all_valid = map(lambda x: x.is_valid(comment), self._plugins)
        return False not in all_valid


class CommentEmailValidator(object):

    def __init__(self, rc, settings):
        pass

    def is_valid(self, comment):
        # Designed to make sure people don't enter random junk for email;
        # not designed to be a serious filter.
        return email_re.match(comment.email) is not None


class CommentURLValidator(object):

    def __init__(self, rc, settings):
        pass

    def is_valid(self, comment):
        # Designed to make sure people don't enter random junk for url;
        # not designed to be a serious filter.
        url = urlparse.urlparse(comment.url)
        return '' not in (url.scheme, url.netloc)


class CommentNameValidator(object):

    def __init__(self, rc, settings):
        pass

    def is_valid(self, comment):
        return comment.name is not ''


class CommentContentValidator(object):

    def __init__(self, rc, settings):
        pass

    def is_valid(self, comment):
        return comment.content is not ''
