from firmant.plugins import resolver_list
from firmant.frontend.atom.resolvers import AtomResolver
from firmant.configuration import settings


def load():
    resolver_list.append(AtomResolver(settings['FRONTEND_ATOM_PREFIX']))
