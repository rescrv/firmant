from firmant.configuration import settings
from firmant.plugins import PluginMount

class AtomProvider(object):
    __metaclass__ = PluginMount

    @classmethod
    def _get_provider(cls):
        provider = filter(lambda m: m.__module__ == settings['ATOM_PROVIDER'],
                          cls.plugins)
        if len(provider) == 0:
            raise RuntimeError('No Atom Provider specified')
        if len(provider) >= 2:
            raise RuntimeError('Multiple Atom Providers available')
        return provider[0]

    class EntryDescriptor(object):

        def __get__(self, instance, owner):
            e = AtomProvider._get_provider().entry
            e.permalink = lambda self: \
                EntryPermalinkProvider.authoritative(self)
            return e

    entry = EntryDescriptor()

    class FeedDescriptor(object):

        def __get__(self, instance, owner):
            f = AtomProvider._get_provider().feed
            f.permalink = lambda self: \
                    FeedPermalinkProvider.authoritative(self)
            return f

    feed = FeedDescriptor()

    class SlugREDescriptor(object):

        def __get__(self, instance, owner):
            s = AtomProvider._get_provider().slug_re
            return s

    slug_re = SlugREDescriptor()


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
