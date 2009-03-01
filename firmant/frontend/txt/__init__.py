from firmant.plugins import resolver_list
from firmant.frontend.txt.resolvers import TxtDateResolver
from firmant.configuration import settings


def load():
    resolver_list.append(TxtDateResolver(settings['FRONTEND_TXT_PREFIX']))
