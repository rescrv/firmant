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
                                                 'ATOM_PROVIDER')
        self._eperma = EntryPermalinkProvider(settings)
        self._fperma = FeedPermalinkProvider(settings)

    def get_entry(self):
        e = self._provider.entry
        e.permalink = lambda e_self: self._eperma.authoritative(e_self)
        return e

    entry = property(get_entry, None, None, "The Atom Entry class")

    def get_feed(self):
        f = self._provider.feed
        f.permalink = lambda f_self: self._fperma.authoritative(f_self)
        return f

    feed = property(get_feed, None, None, "The Atom Feed class")

    def get_slug_re(self):
        return self._provider.slug_re

    slug_re = property(get_slug_re, None, None, "The Atom slug re")


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