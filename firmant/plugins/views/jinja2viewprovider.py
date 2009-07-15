import datetime
from werkzeug.routing import Rule, \
                             Submount
from werkzeug import Response
from werkzeug.exceptions import NotFound
from jinja2 import Environment, \
                   FileSystemLoader

from firmant.datasource.atom import AtomProvider
from firmant.datasource.atom import EntryPermalinkProvider
from firmant.plugins import PluginMount
from firmant.views import ViewProvider
from firmant.filters import FilterProvider


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

        urls = self.rc().get('urls')
        return urls.build(endpoint, values, force_external=True)


class Jinja2GlobalProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def globals_dict(self):
        ret = {}
        for plugin in self.plugins:
            ret.update(self.rc().get(plugin).globals_dict())
        return ret


class Jinja2FrontendViewProvider(ViewProvider):

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
        context['dt']      = dt
        return self.render_response(template, context)

    def XHTML_filter(self, entry):
        rc = self.rc()
        fp = rc.get(FilterProvider)
        entry.summary = fp.filter('XHTML', entry.summary)
        entry.content = fp.filter('XHTML', entry.content)
        return entry

    def render_response(self, template, context):
        loader = FileSystemLoader(self.settings['JINJA2_TEMPLATE_DIR'])
        env = Environment(loader=loader)
        env.globals['MEDIA_PATH'] = self.settings['MEDIA_URL_PATH']
        env.globals.update(self.rc().get(Jinja2GlobalProvider).globals_dict())
        tmpl = env.get_template(template)
        return Response(tmpl.render(context), mimetype='text/html')
