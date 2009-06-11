from firmant.configuration import settings
from firmant.utils import get_module


class PluginMount(type):
    """
    Designed by Marty Alchin in his 'A Simple Plugin Framework' article:
    http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    """

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)


resolver_list = []


def load_plugins():
    for plugin in settings['PLUGINS']:
        try:
            mod = get_module(plugin)
            if hasattr(mod, 'load'):
                mod.load()
                print 'Oldstyle plugin', plugin
        except ImportError:
            raise
