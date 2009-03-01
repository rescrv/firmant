from firmant.plugins import resolver_list
from firmant.frontend.jinja2.resolvers import Jinja2DateResolver
from firmant.configuration import settings


def load():
    resolver_list.append(Jinja2DateResolver(settings['FRONTEND_JINJA2_PREFIX']))
