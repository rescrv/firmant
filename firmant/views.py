from werkzeug.routing import Map, Rule
from werkzeug import Response

from firmant.plugins import PluginMount


class ViewProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    @property
    def enabled(self):
        def enabled_plugin(plugin):
            return str(plugin)[8:-2] in self.settings['ENABLED_VIEWS']
        return filter(enabled_plugin, self.plugins)

    @property
    def url_map(self):
        rc = self.rc()
        objects = map(lambda obj: rc.get(obj), self.enabled)
        rules_l = reduce(lambda x, y: x + y.rules, objects, [])
        return Map(rules_l)

    def get_class(self, klass):
        rc = self.rc()
        potential = filter(lambda c: str(c)[8:-2] == klass, self.enabled)
        if len(potential) < 1:
            return None
        return rc.get(potential[0])


class CatchallProvider(ViewProvider):

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
