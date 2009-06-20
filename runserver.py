#!/usr/bin/python
from optparse import OptionParser
from sys import stderr
import pytz
from werkzeug import script
from werkzeug.script import make_runserver

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

def make_app():
    return Application(settings)

action_runserver = script.make_runserver(make_app, use_reloader=True)

if __name__ == '__main__':
    print 'Starting local WSGI Server'
    print 'Please do not use this server for production'
    script.run()
