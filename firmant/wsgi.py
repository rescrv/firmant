from firmant.configuration import settings
from firmant.plugins import resolver_list


class Request(object):

    def __init__(self, environ=None):
        self.method = environ["REQUEST_METHOD"]
        self.url_prefix = environ["SCRIPT_NAME"]
        self.url = environ["PATH_INFO"]


class Response(object):

    def __init__(self,
            status='200 OK',
            headers=[('content-type', 'text/plain')],
            content=''):
        self.status = status
        self.headers = headers
        self.content = content

    def __eq__(self, other):
        return (self.status == other.status and
                self.headers == other.headers and
                self.content == other.content)


class Application(object):

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        '''
        Proceeds in three stages:
        1. Environ will be parsed into a Request instance.
        2. Handlers are passed the Request until a Response is returned.
        3. The response is returned to the WSGI Server
        '''
        request = Request(self.environ)
        for resolver in resolver_list:
            response = resolver.resolve(request)
            if response != None:
                self.start(response.status, response.headers)
                yield response.content
                return
        self.start('404 Not Found', [('content-type', 'text/plain')])
        yield '404'


configured = False
def application(environ, start_response):
    global configured
    if not configured:
        settings.configure(environ['firmant.settings'])
        configured = True
    return Application(environ, start_response)
