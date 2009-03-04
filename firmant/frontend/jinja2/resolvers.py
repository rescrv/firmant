import datetime
import re
from jinja2 import Environment, FileSystemLoader

from firmant.wsgi import Response
from firmant.resolvers import DateResolver
from firmant.db.atom import Entry
from firmant.db.atom import slug_re
from firmant.configuration import settings


class Jinja2DateResolver(DateResolver):

    def __init__(self, prefix=''):
        super(Jinja2DateResolver, self).__init__(prefix=prefix)
        self.env = Environment(loader=FileSystemLoader(settings['TEMPLATES']))

    def _recent(self, request):
        return Response(content='RECENT')

    def _year(self, request, year):
        try:
            dt = datetime.datetime(int(year), 1, 1)
        except ValueError:
            return None
        entries = Entry.year(dt.year)
        template = self.env.get_template('frontend/year.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries, 'year': dt.year})

    def _month(self, request, year, month):
        try:
            dt = datetime.datetime(int(year), int(month), 1)
        except ValueError:
            return None
        entries = Entry.month(dt.year, dt.month)
        template = self.env.get_template('frontend/month.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries, 'year': dt.year, 'month': dt.month})

    def _day(self, request, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            return None
        entries = Entry.day(dt.year, dt.month, dt.day)
        template = self.env.get_template('frontend/day.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries, 'year': dt.year, 'month': dt.month,
                    'day': dt.day})

    def _single(self, request, slug, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            return None
        if slug_re.match(slug) == None:
            return None
        entry = Entry.single(slug, dt)
        template = self.env.get_template('frontend/single.html')
        return Jinja2DateResolver.generate_response(template,
                {'entry': entry, 'year': dt.year, 'month': dt.month,
                    'day': dt.day, 'slug': slug})

    @staticmethod
    def generate_response(template, variables):
        content = template.render(**variables)
        content = content.encode(settings['FRONTEND_JINJA2_ENCODING'])
        return Response('200 Ok',
                        [('content-type', settings['FRONTEND_JINJA2_MIME'])],
                        content)
