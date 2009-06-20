from werkzeug.exceptions import HTTPException, \
                                InternalServerError

from firmant.views import ViewProvider
from firmant.utils import get_module


class Application(object):

    def __init__(self, settings):
        self.settings = settings
        self.vp       = ViewProvider(settings)
        self.url_map  = self.vp.url_map
        self.views    = {}
        for plugin in settings['PLUGINS']:
            get_module(plugin)

    def __call__(self, environ, start_response):
        urls = self.url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
            klass, func = tuple(endpoint.rsplit('.', 1))
            klass = self.vp.get_class(klass)
            if not hasattr(klass, func):
                raise InternalServerError()
            func = getattr(klass, func)
            if not callable(func):
                raise InternalServerError()
        except HTTPException, e:
            return e(environ, start_response)
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Response was: %s' % func(klass, *args)]
