from werkzeug.routing import Rule, \
                             Submount
from werkzeug import Response
from werkzeug.exceptions import NotFound

from firmant.datasource.atom import AtomProvider
from firmant.datasource.atom import FeedPermalinkProvider
from firmant.views import ViewProvider
from firmant.utils import xml
from firmant.utils import local


class AtomFeedPermalinkProvier(FeedPermalinkProvider):

    def __init__(self, settings):
        self.settings = settings

    def authoritative(self, feed):
        endpoint = __name__ + '.AtomFeedViewProvider.'
        values = {}
        if feed.slug == '':
            endpoint += 'default'
        else:
            endpoint += 'named'
            values['slug']  = feed.slug

        return local.urls.build(endpoint, values, force_external=True)


class AtomFeedViewProvider(ViewProvider):

    def __init__(self, settings):
        self.settings = settings
        self.ap = AtomProvider(settings)

    @property
    def rules(self):
        name = __name__ + '.AtomFeedViewProvider.'
        url_rules = [
            Rule('/', endpoint=name + 'default'),
            Rule('/<slug>/', endpoint=name + 'named'),
        ]
        prefix = self.settings.get('VIEW_ATOM_FEED_PREFIX', '')
        if prefix != '':
            return [Submount('/' + prefix, url_rules)]
        else:
            return url_rules

    def default(self, request):
        return self.common(request, self.ap.feed.default())

    def named(self, request, slug):
        try:
            feed = self.ap.feed.by_slug(slug)
        except ValueError:
            feed = None
        if feed is None:
            return Response('No feed with that name.', status=404,
                    mimetype='text/plain')
        return self.common(request, feed)

    def common(self, request, feed):
        content = xml.etree.tostring(feed.to_xml())
        return Response(content, mimetype='application/atom+xml')
