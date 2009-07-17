from firmant.plugins.views.jinja2viewprovider import Jinja2GlobalProvider
from firmant.datasource.atom import AtomProvider


class RecentEntriesPostedGlobalProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    def globals_dict(self):
        entries, remain = self.rc().get(AtomProvider).entry.recent(limit=5)
        if entries is None:
            return {}
        else:
            permalinks = map(lambda e: (e.title, e.permalink), entries[:5])
            return {'recent_entries': permalinks}


class MonthsPostedGlobalProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    def globals_dict(self):
        months = self.rc().get(AtomProvider).entry.list_months()
        if months is None:
            return {}
        else:
            endpoint = 'firmant.plugins.views.jinja2viewprovider.' + \
                    'Jinja2FrontendViewProvider.month'
            def to_permalink(dt):
                values = {}
                values['year']  = dt.year
                values['month'] = dt.month
                urls = self.rc().get('urls')
                return (dt.strftime('%B %Y'),
                        urls.build(endpoint, values, force_external=True))
            return {'list_months': map(to_permalink, months)}
