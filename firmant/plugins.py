from firmant.configuration import settings
from firmant.db.atom import Entry
from firmant.utils import get_module


resolver_list = []


def load_plugins():
    for plugin in settings['PLUGINS']:
        try:
            mod = get_module(plugin)
            mod.load()
        except ImportError:
            raise
    entry_permalink = get_module(settings['ENTRY_PERMALINK'])
    Entry.set_permalink(entry_permalink.resolvers.entry_permalink)
