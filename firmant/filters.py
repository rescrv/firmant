from firmant.plugins import PluginMount


class FilterProvider(object):
    __metaclass__ = PluginMount

    def __init__(self, settings):
        self.settings = settings

    def filter(self, slot, content):
        plugins = map(lambda obj: obj(self.settings), self.plugins)
        providers = filter(lambda x: x.provides(slot), plugins)
        if len(providers):
            return providers[0].filter(slot, content)
        raise RuntimeError("No filter defines slot '%s'" % slot)
