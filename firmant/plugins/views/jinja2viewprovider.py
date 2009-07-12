import datetime
from werkzeug.routing import Rule, \
                             Submount
from werkzeug import Response
from werkzeug.exceptions import NotFound
from jinja2 import Environment, \
                   FileSystemLoader

from firmant.datasource.atom import AtomProvider
from firmant.datasource.atom import EntryPermalinkProvider
from firmant.views import ViewProvider
from firmant.filters import FilterProvider
from firmant.utils import local


class Jinja2EntryPermalinkProvier(EntryPermalinkProvider):

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def authoritative(self, entry):
        endpoint = __name__ + '.Jinja2FrontendViewProvider.single'
        values = {}
        values['year']  = entry.published.year
        values['month'] = entry.published.month
        values['day']   = entry.published.day
        values['slug']  = entry.slug

        return local.urls.build(endpoint, values, force_external=True)


class Jinja2FrontendViewProvider(ViewProvider):

    def __init__(self, rc, settings):
        super(Jinja2FrontendViewProvider, self).__init__(rc, settings)
        loader = FileSystemLoader(settings['JINJA2_TEMPLATE_DIR'])
        self.env = Environment(loader=loader)
        self.env.globals['MEDIA_PATH'] = settings['MEDIA_URL_PATH']

    @property
    def rules(self):
        name = __name__ + '.Jinja2FrontendViewProvider.'
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
        prefix = self.settings.get('VIEW_JINJA2_FRONTEND_PREFIX', '')
        if prefix != '':
            return [Submount('/' + prefix, url_rules)]
        else:
            return url_rules

    def recent(self, request):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        entries = ap.entry.recent()
        entries = map(self.XHTML_filter, entries)
        context = {}
        context['entries'] = entries
        return self.render_response('frontend/recent.html', context)

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
            raise NotFound('Entry not found.')
        entry = self.XHTML_filter(entry)
        context = {}
        context['entry'] = entry
        context['year']  = year
        context['month'] = month
        context['day']   = day
        context['slug']  = slug
        return self.render_response('frontend/single.html', context)

    def year(self, request, year):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        def func(year, month, day):
            return ap.entry.year(year)
        return self.date_view(func, 'frontend/year.html', year, 1, 1)

    def month(self, request, year, month):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        def func(year, month, day):
            return ap.entry.month(year, month)
        return self.date_view(func, 'frontend/month.html', year, month, 1)

    def day(self, request, year, month, day):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        def func(year, month, day):
            return ap.entry.day(year, month, day)
        return self.date_view(func, 'frontend/day.html', year, month, day)

    def date_view(self, entry_func, template, year, month, day):
        try:
            dt = datetime.datetime(int(year), int(month), int(day))
            entries = entry_func(year, month, day)
        except ValueError:
            entries = None
        if entries is None:
            raise NotFound("Invalid date")
        if entries == []:
            raise NotFound('No entries match.')
        entries = map(self.XHTML_filter, entries)
        context = {}
        context['entries'] = entries
        context['year']    = dt.year
        context['month']   = dt.month
        context['day']     = dt.day
        return self.render_response(template, context)

    def XHTML_filter(self, entry):
        rc = self.rc()
        fp = rc.get(FilterProvider)
        entry.summary = fp.filter('XHTML', entry.summary)
        entry.content = fp.filter('XHTML', entry.content)
        return entry

    def render_response(self, template, context):
        tmpl = self.env.get_template(template)
        return Response(tmpl.render(context), mimetype='text/html')
