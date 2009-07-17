from werkzeug.routing import Map, Rule
from werkzeug import Response

from firmant.plugins import MultiProviderPlugin


class ViewProvider(MultiProviderPlugin):

    providers_setting = 'VIEWS'

    @property
    def url_map(self):
        rules_l = reduce(lambda x, y: x + y.rules, self._plugins, [])
        return Map(rules_l)

    def get_class(self, klass):
        def classname(instance):
            return str(instance.__class__)[8:-2]
        potential = filter(lambda c: classname(c) == klass, self._plugins)
        if len(potential) < 1:
            return None
        return potential[0]


class CatchallProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    @property
    def rules(self):
        url_rules = [
            Rule('/', endpoint=__name__ + '.CatchallProvider.catchall',
                defaults={"p": ''}),
            Rule('/<path:p>', endpoint=__name__ + '.CatchallProvider.catchall')
        ]
        return url_rules

    def catchall(self, request, p):
        return Response('''If you're reading this the catchall provider
            functions well on your system (%s).''' % p, mimetype='text/plain')
