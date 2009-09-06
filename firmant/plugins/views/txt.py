import datetime
from werkzeug.routing import Rule, \
                             Submount
from werkzeug import Response
from werkzeug.exceptions import NotFound

from firmant.datasource.atom import AtomProvider
from firmant.datasource.atom import slug_re


class TxtFrontendViewProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

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

    def common(self, entry_func, year, month, day):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
            entries = entry_func(ap, dt.year, dt.month, dt.day)
        except ValueError:
            entries = None
        if entries is None:
            return Response('Invalid date', status=404, mimetype='text/plain')
        if entries == []:
            return Response('No entries match.', status=404,
                    mimetype='text/plain')
        return Response(repr(entries), mimetype='text/plain')

    def year(self, request, year):
        entry_func = lambda ap, y, m, d: ap.entry.year(y)
        return self.common(entry_func, year, 1, 1)

    def month(self, request, year, month):
        entry_func = lambda ap, y, m, d: ap.entry.month(y, m)
        return self.common(entry_func, year, month, 1)

    def day(self, request, year, month, day):
        entry_func = lambda ap, y, m, d: ap.entry.day(y, m, d)
        return self.common(entry_func, year, month, day)

    def single(self, request, slug, year, month, day):
        def entry_func(ap, y, m, d):
            if slug_re.match(slug) == None:
                return []
            else:
                return ap.entry.single(slug, y, m, d)
        return self.common(entry_func, year, month, day)
