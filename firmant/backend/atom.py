from firmant.plugins import PluginMount
from firmant.configuration import settings

class AtomProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        provider = filter(lambda m: m.__module__ == \
                          settings['ATOM_PROVIDER'],
                          self.plugins)
        if len(provider) < 1:
            raise RuntimeError('No Atom Provider specified')
        if len(provider) > 1:
            raise RuntimeError('Multiple Atom Providers available')

        self._provider = provider[0]
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
        provider = filter(lambda m: m.__module__ == \
                          settings['ENTRY_PERMALINK'],
                          self.plugins)
        if len(provider) < 1:
            raise RuntimeError('No Entry Permalink Provider specified')
        if len(provider) > 1:
            raise RuntimeError('Multiple Entry Permalink Providers available')

        self._provider = provider[0](settings)

    def authoritative(self, entry):
        return self._provider.authoritative(entry)


class FeedPermalinkProvider(object):

    __metaclass__ = PluginMount

    def __init__(self, settings):
        provider = filter(lambda m: m.__module__ == \
                          settings['FEED_PERMALINK'],
                          self.plugins)
        if len(provider) < 1:
            raise RuntimeError('No Feed Permalink Provider specified')
        if len(provider) > 1:
            raise RuntimeError('Multiple Feed Permalink Providers available')

        self._provider = provider[0](settings)

    def authoritative(self, feed):
        return self._provider.authoritative(feed)
