from firmant.configuration import settings
from firmant.db.atom import Entry


resolver_list = []


def get_module(plugin):
    try:
        modules = plugin.split('.')
        mod = __import__(plugin, {}, {}, [])
        for module in modules[1:]:
            mod = getattr(mod, module)
        return mod
    except ImportError:
        raise


def load_plugins():
    for plugin in settings['PLUGINS']:
        try:
            mod = get_module(plugin)
            mod.load()
        except ImportError:
            raise
    entry_permalink = get_module(settings['ENTRY_PERMALINK'])
    Entry.set_permalink(entry_permalink.resolvers.entry_permalink)
