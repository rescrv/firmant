from werkzeug.routing import Rule, \
                             Submount
from werkzeug import Response
from werkzeug.exceptions import NotFound

from firmant.datasource.atom import AtomProvider
from firmant.filters import FilterProvider
from firmant.utils import xml


class AtomFeedPermalinkProvider(object):

    def __init__(self, rc, settings):
        self.rc = rc
        self.settings = settings

    def authoritative(self, slug):
        endpoint = __name__ + '.AtomFeedViewProvider.'
        values = {}
        if slug == '':
            endpoint += 'default'
        else:
            endpoint += 'named'
            values['slug']  = slug

        urls = self.rc().get('urls')
        return urls.build(endpoint, values, force_external=True)


class AtomFeedViewProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

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
        rc = self.rc()
        ap = rc.get(AtomProvider)
        return self.common(request, ap.feed.default())

    def named(self, request, slug):
        rc = self.rc()
        ap = rc.get(AtomProvider)
        try:
            feed = ap.feed.by_slug(slug)
        except ValueError:
            feed = None
        if feed is None:
            return Response('No feed with that name.', status=404,
                    mimetype='text/plain')
        return self.common(request, feed)

    def common(self, request, feed):
        rc = self.rc()
        fp = rc.get(FilterProvider)
        def filter(content):
            open_div = '<div xmlns="http://www.w3.org/1999/xhtml">'
            close_div = '</div>'
            filtered_content = fp.filter('XHTML', content)
            return xml.etree.fromstring(open_div + filtered_content + close_div)
        content = xml.etree.tostring(feed.to_xml(filter))
        return Response(content, mimetype='application/atom+xml')
