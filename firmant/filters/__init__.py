from firmant.plugins import PluginMount


class FilterProvider(object):
    __metaclass__ = PluginMount

    @classmethod
    def filter(cls, slot, content):
        providers = filter(lambda x: x.provides(slot), cls.plugins)
        if len(providers):
            return providers[0]().filter(slot, content)
        raise RuntimeError("No filter defines slot '%s'" % slot)
