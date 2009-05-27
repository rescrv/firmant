from firmant.plugins import PluginMount


class FilterProvider(object):
    __metaclass__ = PluginMount

    @classmethod
    def filter(cls, slot, content):
        providers = filter(lambda x: slot in x.provides(), cls.plugins)
        if len(providers):
            return providers[0].filter(slot, content)
        raise RuntimeError("No filter defines slot '%s'" % slot)

    @classmethod
    def provides(cls):
        provides = reduce(lambda x, y: x + y, cls.plugins)
        return provides
