#!/usr/bin/python
from wsgiref.simple_server import make_server
from optparse import OptionParser
from sys import stderr
import socket
import pytz

from firmant.wsgi import Application
from firmant.utils import mod_to_dict
from firmant.utils import get_module

parser = OptionParser()
parser.add_option('-s', '--settings',
        dest='settings', type='string', default='settings',
        help='the settings module to use for the test server.')
parser.add_option('-p', '--port',
        dest='port', type='int', default='8080',
        help='the port on which to run the test server.')
parser.add_option('-H', '--host',
        dest='host', type='string', default='',
        help='the host to which the server should bind.')
(options, args) = parser.parse_args()

try:
    settings = mod_to_dict(get_module(options.settings))
except ImportError:
    stderr.write('Please specify a settings module that can be imported.\n')
    exit(1)

try:
    server = make_server(options.host, options.port, Application(settings))
except socket.error:
    stderr.write('Please specify a host/port to which you may bind (the '
                 'defaults usually work well)\n')
    exit(1)


if __name__ == '__main__':
    print 'Starting local WSGI Server'
    print 'Please do not use this server for production'
    print 'Settings: %s' % options.settings
    print 'Bound to: http://%s:%i/' % (options.host, options.port)
    print '============================================'
    server.serve_forever()
