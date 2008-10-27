#!/usr/bin/python
from wsgiref.simple_server import make_server
from firmant import Application

make_server('', 8080, Application).serve_forever()
