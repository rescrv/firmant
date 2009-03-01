from firmant.configuration import settings


resolver_list = []

def load_plugins():
    for plugin in settings['PLUGINS']:
        try:
            modules = plugin.split('.')
            mod = __import__(plugin, {}, {}, [])
            for module in modules[1:]:
                mod = getattr(mod, module)
            mod.load()
        except ImportError:
            raise
