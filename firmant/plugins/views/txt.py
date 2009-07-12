import datetime
from werkzeug.routing import Rule, \
                             Submount
from werkzeug import Response
from werkzeug.exceptions import NotFound

from firmant.datasource.atom import AtomProvider
from firmant.views import ViewProvider


class TxtFrontendViewProvider(ViewProvider):

    @property
    def rules(self):
        name = __name__ + '.TxtFrontendViewProvider.'
        url_rules = [
            Rule('/', endpoint=name + 'recent'),
            Rule('/<int(fixed_digits=4):year>/', endpoint=name + 'year'),
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>/',
                 endpoint=name + 'month'),
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>' + \
                 '/<int(fixed_digits=2):day>/', endpoint=name + 'day'),
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>' + \
                 '/<int(fixed_digits=2):day>/<slug>', endpoint=name + 'single')
        ]
        prefix = self.settings.get('VIEW_TXT_FRONTEND_PREFIX', '')
        if prefix != '':
            return [Submount('/' + prefix, url_rules)]
        else:
            return url_rules

    def recent(self, request):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        entries = ap.entry.recent()
        return Response(repr(entries), mimetype='text/plain')

    def year(self, request, year):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        try:
            dt = datetime.datetime(int(year), 1, 1)
            entries = ap.entry.year(dt.year)
        except ValueError:
            entries = None
        if entries is None:
            return Response('Invalid date', status=404, mimetype='text/plain')
        if entries == []:
            return Response('No entries match.', status=404,
                    mimetype='text/plain')
        return Response(repr(entries), mimetype='text/plain')

    def month(self, request, year, month):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        try:
            dt = datetime.datetime(int(year), int(month), 1)
            entries = ap.entry.month(dt.year, dt.month)
        except ValueError:
            entries = None
        if entries is None:
            return Response('Invalid date', status=404, mimetype='text/plain')
        if entries == []:
            return Response('No entries match.', status=404,
                    mimetype='text/plain')
        return Response(repr(entries), mimetype='text/plain')

    def day(self, request, year, month, day):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
            entries = ap.entry.day(dt.year, dt.month, dt.day)
        except ValueError:
            entries = None
        if entries is None:
            return Response('Invalid date', status=404, mimetype='text/plain')
        if entries == []:
            return Response('No entries match.', status=404,
                    mimetype='text/plain')
        return Response(repr(entries), mimetype='text/plain')

    def single(self, request, slug, year, month, day):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
            if ap.slug_re.match(slug) == None:
                entry = None
            else:
                entry = ap.entry.single(slug, dt.year, dt.month, dt.day)
        except ValueError:
            entry = None
        if entry is None:
            return Response('Not found.', status=404, mimetype='text/plain')
        return Response(repr(entry), mimetype='text/plain')
