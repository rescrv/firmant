from firmant.plugins import PluginMount


def select_canonical_plugin(plugins, settings, config_var):
    provider = filter(lambda m: m.__module__ == settings[config_var], plugins)
    if len(provider) < 1:
        raise RuntimeError('No plugin for "%s" specified' % config_var)
    if len(provider) > 1:
        raise RuntimeError('Multiple plugins for "%s" available' % config_var)
    return provider[0]


class AtomProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'ATOM_PROVIDER')(settings)

    entry   = property(lambda self: self._provider.entry,
                       doc="The Atom Entry class")

    feed    = property(lambda self: self._provider.feed,
                       doc="The Atom Feed class")

    slug_re = property(lambda self: self._provider.slug_re,
                       doc="The Atom slug re")


class EntryPermalinkProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'ENTRY_PERMALINK')(settings)

    def authoritative(self, entry):
        return self._provider.authoritative(entry)


class FeedPermalinkProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        self._provider = select_canonical_plugin(self.plugins,
                                                 settings,
                                                 'FEED_PERMALINK')(settings)

    def authoritative(self, feed):
        return self._provider.authoritative(feed)
