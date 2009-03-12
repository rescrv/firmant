import re

from firmant.wsgi import Response
from firmant.resolvers import Resolver
from firmant.db.atom import Entry
from firmant.configuration import settings


class AtomResolver(Resolver):

    def __init__(self, prefix=''):
        if prefix == '':
            prefix = '^/'
        else:
            prefix = '^/' + prefix + '/'
        self.named_re = re.compile(prefix + '(?P<slug>[-_a-zA-Z0-9]{1,96})/$')
        self.default_re = re.compile(prefix + '$')

    def resolve(self, request):
        default = self.default_re.match(request.url)
        named = self.named_re.match(request.url)
        if default != None:
            return Response(content='default atom')
        elif named != None:
            return Response(content='named atom')
        return None
