from firmant.utils import get_module


def load_plugin(full_path):
    module_name = '.'.join(full_path.split('.')[:-1])
    object_name = full_path.split('.')[-1]
    module      = get_module(module_name)

    if not hasattr(module, object_name):
        raise AttributeError('Module "%s" has no attribute "%s"' % \
                (module_name, object_name))

    plugin = getattr(module, object_name)
    return plugin


class SingleProviderPlugin(object):

    def __init__(self, rc, settings):
        self.rc        = rc
        self.settings  = settings
        full_path      = settings.get(self.provider_setting, None)
        if full_path is None:
            raise ValueError('Please set "%s"', self.provider_setting)
        plugin         = load_plugin(full_path)
        self._provider = plugin(rc, settings)


class MultiProviderPlugin(object):

    def __init__(self, rc, settings):
        self.rc        = rc
        self.settings  = settings

        plugin_list    = self.settings.get(self.providers_setting, None)
        if plugin_list is None:
            raise ValueError('Please set "%s"', self.providers_setting)

        plugin_objects = map(load_plugin, plugin_list)
        self._plugins  = map(lambda x: x(rc, settings), plugin_objects)
