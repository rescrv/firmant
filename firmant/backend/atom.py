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

    def get_entry(self):
        e = self._provider.entry
        e.permalink = lambda self: EntryPermalinkProvider.authoritative(self)
        return e

    entry = property(get_entry, None, None, "The Atom Entry class")

    def get_feed(self):
        f = self._provider.feed
        f.permalink = lambda self: FeedPermalinkProvider.authoritative(self)
        return f

    feed = property(get_feed, None, None, "The Atom Feed class")

    def get_slug_re(self):
        return self._provider.slug_re

    slug_re = property(get_slug_re, None, None, "The Atom slug re")


class EntryPermalinkProvider(object):
    __metaclass__ = PluginMount

    @classmethod
    def authoritative(cls, entry):
        import firmant.frontend.jinja2.resolvers
        provider = filter(lambda m: m.__module__ == settings['ENTRY_PERMALINK'],
                          cls.plugins)
        if len(provider) == 0:
            raise RuntimeError('No Entry Permalink Provider specified')
        if len(provider) >= 2:
            raise RuntimeError('Multiple Entry Permalink Providers available')
        return provider[0].authoritative(entry)


class FeedPermalinkProvider(object):
    __metaclass__ = PluginMount

    @classmethod
    def authoritative(cls, feed):
        provider = filter(lambda m: m.__module__ == settings['FEED_PERMALINK'],
                          cls.plugins)
        if len(provider) == 0:
            raise RuntimeError('No Feed Permalink Provider specified')
        if len(provider) >= 2:
            raise RuntimeError('Multiple Feed Permalink Providers available')
        return provider[0].authoritative(feed)
