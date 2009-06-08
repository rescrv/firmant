import datetime
import re

from firmant.wsgi import Response
from firmant.resolvers import DateResolver
from firmant.backend.atom import AtomProvider
from firmant.configuration import settings


class TxtDateResolver(DateResolver):

    def _recent(self, request):
        entries = AtomProvider(settings).entry.recent()
        return Response(content=entries.__repr__())

    def _year(self, request, year):
        try:
            dt = datetime.datetime(int(year), 1, 1)
        except ValueError:
            return None
        entries = AtomProvider(settings).entry.year(dt.year)
        return Response(content=entries.__repr__())

    def _month(self, request, year, month):
        try:
            dt = datetime.datetime(int(year), int(month), 1)
        except ValueError:
            return None
        entries = AtomProvider(settings).entry.month(dt.year, dt.month)
        return Response(content=entries.__repr__())

    def _day(self, request, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            return None
        entries = AtomProvider(settings).entry.day(dt.year, dt.month, dt.day)
        return Response(content=entries.__repr__())

    def _single(self, request, slug, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            return None
        if AtomProvider(settings).slug_re.match(slug) == None:
            return None
        entries = AtomProvider(settings).entry.single(slug, dt)
        return Response(content=entries.__repr__())
