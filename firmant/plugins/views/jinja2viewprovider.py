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


class Jinja2EntryPermalinkProvider(EntryPermalinkProvider):

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

    class MultiPageList(object):

        def __init__(self, rc, settings, func, page=0):
            self.settings = settings
            self.rc = rc

            self.func   = func
            self.limit  = settings.get('JINJA2_ENTRIES_PER_PAGE', 10)
            self.offset = page * self.limit
            self.page   = page

        def __call__(self):
            entries, self.remain = self.func(self.limit, self.offset)
            return entries

        @property
        def has_older(self):
            return self.remain > 0

        @property
        def has_newer(self):
            return self.offset > 0

        def _common(self, page=None):
            rc = self.rc()
            urls         = rc.get('urls')
            endpoint     = rc.get('endpoint')
            args         = rc.get('args').copy()
            if page is not None:
                args['page'] = page
            return urls.build(endpoint, args, force_external=True)

        @property
        def newer(self):
            if self.has_newer:
                if self.page == 1:
                    return self._common()
                return self._common(self.page - 1)
            return None

        @property
        def older(self):
            if self.has_older:
                return self._common(self.page + 1)
            return None

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
        try:
            page = int(request.args.get('page', 0))
        except ValueError:
            page = 0
        func = lambda limit, offset: ap.entry.recent(limit, offset)
        MPL = self.MultiPageList(self.rc, self.settings, func, page)
        entries = MPL()
        entries = map(self.XHTML_filter, entries)
        context = {}
        context['entries'] = entries
        context['page']    = MPL
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
        def func(year, month, day, limit, offset):
            return ap.entry.year(year, limit=limit, offset=offset)
        template = 'frontend/year.html'
        return self.date_view(request, func, template, year, 1, 1)

    def month(self, request, year, month):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        def func(year, month, day, limit, offset):
            return ap.entry.month(year, month, limit=limit, offset=offset)
        template = 'frontend/month.html'
        return self.date_view(request, func, template, year, month, 1)

    def day(self, request, year, month, day):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        def func(year, month, day, limit, offset):
            return ap.entry.day(year, month, day, limit=limit, offset=offset)
        template = 'frontend/day.html'
        return self.date_view(request, func, template, year, month, day)

    def date_view(self, request, entry_func, template, year, month, day):
        try:
            try:
                page = int(request.args.get('page', 0))
            except ValueError:
                page = 0
            dt = datetime.datetime(int(year), int(month), int(day))
            func = lambda limit, offset: entry_func(dt.year, dt.month,
                    dt.day, limit, offset)
            MPL = self.MultiPageList(self.rc, self.settings, func, page)
            entries = MPL()
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
        context['page']    = MPL
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
