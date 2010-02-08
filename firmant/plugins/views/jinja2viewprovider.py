import datetime
from werkzeug import Response
from werkzeug.exceptions import NotFound
from jinja2 import Environment, \
                   FileSystemLoader

from firmant.plugins import MultiProviderPlugin
from firmant.views.generic import GenericEntryViewProvider
from firmant.views.generic import GenericCategoryViewProvider
from firmant.filters import FilterProvider


class Jinja2EntryPermalinkProvider(object):

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def authoritative(self, slug, published):
        endpoint = __name__ + '.Jinja2FrontendViewProvider.single'
        values = {}
        values['year']  = published.year
        values['month'] = published.month
        values['day']   = published.day
        values['slug']  = slug

        urls = self.rc().get('urls')
        return urls.build(endpoint, values, force_external=True)


class Jinja2GlobalProvider(MultiProviderPlugin):

    providers_setting = 'JINJA2_GLOBALS'

    def globals_dict(self):
        ret = {}
        for plugin in self._plugins:
            ret.update(plugin.globals_dict())
        return ret


class Jinja2FrontendViewProvider(GenericEntryViewProvider):

    @property
    def prefix(self):
        return self.settings.get('VIEW_JINJA2_FRONTEND_PREFIX', '')

    @property
    def limit(self):
        return self.settings.get('JINJA2_ENTRIES_PER_PAGE')

    def _recent(self, request, entries, page):
        entries = map(self.XHTML_filter, entries)
        context = {}
        context['entries'] = entries
        context['page']    = page
        return self.render_response('frontend/recent.html', context)

    def _single(self, request, entry):
        entry = self.XHTML_filter(entry)
        context = {}
        context['entry'] = entry
        return self.render_response('frontend/single.html', context)

    def _year(self, request, entries, page, year):
        return self.render('frontend/year.html', entries, page,
                datetime.date(year, 1, 1))

    def _month(self, request, entries, page, year, month):
        return self.render('frontend/year.html', entries, page,
                datetime.date(year, month, 1))

    def _day(self, request, entries, page, year, month, day):
        return self.render('frontend/year.html', entries, page,
                datetime.date(year, month, day))

    def XHTML_filter(self, entry):
        rc = self.rc()
        fp = rc.get(FilterProvider)
        entry.summary = fp.filter('XHTML', entry.summary)
        entry.content = fp.filter('XHTML', entry.content)
        return entry

    def render(self, template, entries, page, d):
        entries = map(self.XHTML_filter, entries)
        context = {}
        context['entries'] = entries
        context['page']    = page
        context['dt']      = d
        return self.render_response(template, context)

    def render_response(self, template, context):
        loader = FileSystemLoader(self.settings['JINJA2_TEMPLATE_DIR'])
        env = Environment(loader=loader)
        env.globals['MEDIA_PATH'] = self.settings['MEDIA_URL_PATH']
        env.globals.update(self.rc().get(Jinja2GlobalProvider).globals_dict())
        tmpl = env.get_template(template)
        return Response(tmpl.render(context), mimetype='text/html')


class Jinja2CategoryViewProvider(GenericCategoryViewProvider):

    @property
    def prefix(self):
        return self.settings.get('VIEW_JINJA2_CATEGORY_PREFIX', '')

    @property
    def limit(self):
        return self.settings.get('JINJA2_ENTRIES_PER_PAGE')

    def _categories(self, request, categories):
        context = {}
        context['categories'] = categories
        return self.render_response('frontend/categories.html', context)

    def _single(self, request, slug, entries, page):
        context = {}
        context['slug']    = slug
        context['entries'] = entries
        context['page']    = page
        return self.render_response('frontend/category_list.html', context)

    def render_response(self, template, context):
        loader = FileSystemLoader(self.settings['JINJA2_TEMPLATE_DIR'])
        env = Environment(loader=loader)
        env.globals['MEDIA_PATH'] = self.settings['MEDIA_URL_PATH']
        env.globals.update(self.rc().get(Jinja2GlobalProvider).globals_dict())
        tmpl = env.get_template(template)
        return Response(tmpl.render(context), mimetype='text/html')
