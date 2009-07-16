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

class SingleProviderPlugin(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

        full_path = settings.get(self.provider_setting, None)

        if full_path is None:
            raise ValueError('Please set "%s"', self.provider_setting)

        module_name = '.'.join(full_path.split('.')[:-1])
        object_name = full_path.split('.')[-1]
        module      = get_module(module_name)

        if not hasattr(module, object_name):
            raise AttributeError('Module "%s" has no attribute "%s"' % \
                    (module_name, object_name))

        plugin = getattr(module, object_name)

        self._provider = plugin(rc, settings)
