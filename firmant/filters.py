from firmant.plugins import MultiProviderPlugin


class FilterProvider(MultiProviderPlugin):

    providers_setting = 'TEXT_FILTERS'

    def filter(self, slot, content):
        providers = filter(lambda o: o.provides(slot), self._plugins)
        if len(providers):
            return providers[0].filter(slot, content)
        raise RuntimeError("No filter defines slot '%s'" % slot)
