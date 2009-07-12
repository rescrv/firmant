import weakref
from werkzeug import Request, \
                     SharedDataMiddleware, \
                     ClosingIterator
from werkzeug.exceptions import HTTPException, \
                                InternalServerError

from firmant.views import ViewProvider
from firmant.utils import get_module
from firmant.utils import local
from firmant.utils import local_manager


class RequestContext(object):

    default = 'default'

    def __init__(self, settings):
        self.settings = settings
        self.objects = {}
        self.weakref = weakref.ref(self)

    def get(self, cls):
        try:
            return self.objects[cls]
        except KeyError:
            self.objects[cls] = cls(self.weakref, self.settings)
            return self.objects[cls]

    def set(self, cls, value):
        self.objects[cls] = value


class Application(object):

    def __init__(self, settings):
        for plugin in settings['PLUGINS']:
            get_module(plugin)
        self.settings = settings

        if settings.get('MEDIA_FS_PATH', None) != None:
            self.dispatch = SharedDataMiddleware(self.dispatch,
                     {settings['MEDIA_URL_PATH']: settings['MEDIA_FS_PATH']})

    def dispatch(self, environ, start_response):
        rc = RequestContext(self.settings)
        request = Request(environ)
        rc.set(Request, request)

        vp = rc.get(ViewProvider)
        url_map = vp.url_map

        local.urls = urls = url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
            klass, func = tuple(endpoint.rsplit('.', 1))
            klass = vp.get_class(klass)
            if not hasattr(klass, func):
                raise InternalServerError()
            func = getattr(klass, func)
            if not callable(func):
                raise InternalServerError()
            response = func(request, **args)
        except HTTPException, e:
            return e(environ, start_response)
        return ClosingIterator(response(environ, start_response),
                [local_manager.cleanup])

    def __call__(self, environ, start_response):
        return self.dispatch(environ, start_response)
