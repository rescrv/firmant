import datetime
import re
import urlparse
from jinja2 import Environment, FileSystemLoader

from firmant.wsgi import Response
from firmant.resolvers import DateResolver
from firmant.datasource.atom import AtomProvider
from firmant.filters import FilterProvider
from firmant.configuration import settings
from firmant.datasource.atom import EntryPermalinkProvider


class Jinja2EntryPermalink(EntryPermalinkProvider):

    def __init__(self, settings):
        self.settings = settings

    def authoritative(self, entry):
        prefix = '/' + self.settings['FRONTEND_JINJA2_PREFIX']
        if prefix == '/':
            prefix = ''
        path = '%s/%s/%s/' % (prefix, entry.published.strftime('%Y/%m/%d'),
                              entry.slug)
        return urlparse.urljoin(self.settings['HOST'], path)


class Jinja2DateResolver(DateResolver):

    def __init__(self, prefix=''):
        super(Jinja2DateResolver, self).__init__(prefix=prefix)
        self.env = Environment(loader=FileSystemLoader(settings['TEMPLATES']))

    def _recent(self, request):
        entries = AtomProvider(settings).entry.recent()
        entries = map(Jinja2DateResolver.XHTML_filter, entries)
        template = self.env.get_template('frontend/recent.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries})

    def _year(self, request, year):
        try:
            dt = datetime.datetime(int(year), 1, 1)
        except ValueError:
            return None
        entries = AtomProvider(settings).entry.year(dt.year)
        entries = map(Jinja2DateResolver.XHTML_filter, entries)
        template = self.env.get_template('frontend/year.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries, 'year': dt.year})

    def _month(self, request, year, month):
        try:
            dt = datetime.datetime(int(year), int(month), 1)
        except ValueError:
            return None
        entries = AtomProvider(settings).entry.month(dt.year, dt.month)
        entries = map(Jinja2DateResolver.XHTML_filter, entries)
        template = self.env.get_template('frontend/month.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries, 'year': dt.year, 'month': dt.month})

    def _day(self, request, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            return None
        entries = AtomProvider(settings).entry.day(dt.year, dt.month, dt.day)
        entries = map(Jinja2DateResolver.XHTML_filter, entries)
        template = self.env.get_template('frontend/day.html')
        return Jinja2DateResolver.generate_response(template,
                {'entries': entries, 'year': dt.year, 'month': dt.month,
                    'day': dt.day})

    def _single(self, request, slug, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
        except ValueError:
            return None
        if AtomProvider(settings).slug_re.match(slug) == None:
            return None
        entry = AtomProvider(settings).entry.single(slug, dt)
        entry = Jinja2DateResolver.XHTML_filter(entry)
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

    @staticmethod
    def XHTML_filter(entry):
        fp = FilterProvider(settings)
        entry.summary = fp.filter('XHTML', entry.summary)
        entry.content = fp.filter('XHTML', entry.content)
        return entry
