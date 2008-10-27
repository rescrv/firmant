class Application(object):
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        status = '200 OK'
        headers = [('content-type', 'text/plain')]
        self.start(status, headers)
        yield "Hello World\n"
