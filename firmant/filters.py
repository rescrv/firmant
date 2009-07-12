from firmant.plugins import PluginMount


class FilterProvider(object):
    __metaclass__ = PluginMount

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def filter(self, slot, content):
        rc = self.rc()
        providers = filter(lambda o: rc.get(o).provides(slot), self.plugins)
        if len(providers):
            return rc.get(providers[0]).filter(slot, content)
        raise RuntimeError("No filter defines slot '%s'" % slot)
