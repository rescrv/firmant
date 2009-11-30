from pytz import utc
from werkzeug.contrib.atom import AtomFeed
from werkzeug.contrib.atom import FeedEntry

from firmant.views.generic import GenericFeedViewProvider
from firmant.filters import FilterProvider


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


class AtomFeedViewProvider(GenericFeedViewProvider):

    @property
    def prefix(self):
        return self.settings.get('VIEW_ATOM_FEED_PREFIX', '')

    def render(self, request, feed):
        rc = self.rc()
        fp = rc.get(FilterProvider)
        params = {}
        params['title'] = feed.title
        params['title_type'] = 'text'
        params['feed_url'] = params['id'] = feed.permalink
        params['generator'] = ('Firmant', 'http://firmant.org/', None)
        params['updated'] = feed.updated
        params['rights'] = feed.rights
        params['rights_type'] = 'text'
        params['subtitle'] = feed.subtitle
        params['subtitle_type'] = 'text'
        af = AtomFeed(**params)
        for entry in feed.entries:
            params = {}
            params['title'] = entry.title
            params['title_type'] = 'text'
            params['content'] = fp.filter('XHTML', entry.content)
            params['content_type'] = 'xhtml'
            params['summary'] = fp.filter('XHTML', entry.summary)
            params['summary_type'] = 'xhtml'
            params['author'] = {}
            params['author']['name'] = entry.author.name
            if entry.author.uri is not None:
                params['author']['uri'] = entry.author.uri
            if entry.author.email is not None:
                params['author']['email'] = entry.author.email
            params['rights'] = entry.rights
            params['rights_type'] = 'text'
            params['url'] = params['id'] = entry.permalink
            params['updated'] = entry.updated.astimezone(utc)
            params['published'] = entry.published.astimezone(utc)
            af.add(FeedEntry(**params))
        return af.get_response()
