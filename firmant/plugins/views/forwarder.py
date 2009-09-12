from werkzeug.routing import Rule
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect


class UrlAliasViewProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    @property
    def rules(self):
        endpoint = __name__ + '.UrlAliasViewProvider.redirect'

        url_rules = []
        for key, value in self.settings['URL_ALIASES'].iteritems():
            url_rules.append(Rule(key, endpoint=endpoint))
        return url_rules

    def redirect(self, request):
        url  = self.settings['URL_ALIASES'][request.path][1]
        code = self.settings['URL_ALIASES'][request.path][0]
        return redirect(url, code=code)
