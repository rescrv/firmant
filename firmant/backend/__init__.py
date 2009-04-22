from firmant.configuration import settings
from firmant.utils import get_module

def get_atom_module():
    return get_module(settings['ATOM_MODULE'])

def get_entry_class():
    atom = get_atom_module()
    return atom.Entry

def get_feed_class():
    atom = get_atom_module()
    return atom.Feed
