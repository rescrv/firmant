import datetime
import urlparse
import urllib
import re
from werkzeug import Request
from werkzeug import Response
from werkzeug.exceptions import MethodNotAllowed
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import InternalServerError
from werkzeug.routing import Rule, \
                             Submount
from werkzeug.utils import redirect

from firmant.csrf import CSRFTokenProvider
from firmant.datasource.atom import AtomProvider
from firmant.datasource.atom import EntryPermalinkProvider
from firmant.datasource.comments import Comment
from firmant.datasource.comments import CommentProvider
from firmant.datasource.comments import CommentValidator
from firmant.plugins.views.jinja2viewprovider import Jinja2FrontendViewProvider


class CommentDataGlobalProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    def globals_dict(self):
        rc = self.rc()
        def comment_post_url(published, slug):
            endpoint = __name__ + '.CommentSubmissionHandler.post'
            values = {}
            values['year']  = published.year
            values['month'] = published.month
            values['day']   = published.day
            values['slug']  = slug

            urls = rc.get('urls')
            return urls.build(endpoint, values, force_external=True)
        ret = {}
        ret['comment_post_url'] = comment_post_url
        enabled = self.settings.get('COMMENT_SUBMISSION_ENABLED', False)
        ret['comments_enabled'] = enabled
        ret['comments_for_entry'] = rc.get(CommentProvider).for_entry

        request = rc.get(Request)
        ret['comment_name']    = request.args.get('name', '')
        ret['comment_email']   = request.args.get('email', '')
        ret['comment_url']     = request.args.get('url', '')
        ret['comment_comment'] = request.args.get('comment', '')
        ret['comment_message'] = request.args.get('message', '')
        return ret


class CommentSubmissionHandler(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    @property
    def rules(self):
        name = __name__ + '.CommentSubmissionHandler.'
        url_rules = [
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>' + \
                 '/<int(fixed_digits=2):day>/<slug>', endpoint=name + 'post')
        ]
        prefix = self.settings.get('COMMENT_SUBMISSION_PREFIX', '')
        if prefix != '':
            return [Submount('/' + prefix, url_rules)]
        else:
            return url_rules

    def post(self, request, slug, year, month, day):
        rc = self.rc()

        # Verify appropriate http method.
        if not request.method == 'POST':
            return self.method_not_allowed()

        # Check that comments are enabled
        if not self.settings.get('COMMENT_SUBMISSION_ENABLED', False):
            return self.comments_disabled()

        # Check that entry exists
        if not rc.get(AtomProvider).entry.exists(slug, year, month, day):
            return self.entry_doesnot_exist()

        # Create comment object
        c = Comment()
        try:
            c.name       = request.form.get('name')
            c.email      = request.form.get('email')
            c.url        = request.form.get('url')
            c.ip         = request.remote_addr
            c.useragent  = request.user_agent
            c.created    = datetime.datetime.utcnow()
            c.content    = request.form.get('comment')
            c.status     = self.settings['COMMENT_STATUS_DEFAULT']
            c.entry_pkey = \
                    (datetime.date(int(year), int(month), int(day)), slug)
        except ValueError:
            return self.invalid_data(request, c)
        comment_validator = self.rc().get(CommentValidator)
        if not comment_validator.is_valid(c):
            return self.invalid_data(request, c)

        # Check for valid csrf token.
        csrf_token = request.form.get('csrf_token', '')
        ip_addr    = request.remote_addr
        if not rc.get(CSRFTokenProvider).consume_token(csrf_token, ip_addr):
            return self.invalid_csrf_token(request, c)

        # Store comment object
        comment_provider = rc.get(CommentProvider)
        try:
            comment_provider.save(c)
        except CommentProvider.UniqueViolationError:
            return self.unique_error(c)
        except CommentProvider.StorageError:
            return self.storage_error()

        return self.success(c)

    def method_not_allowed(self):
        raise MethodNotAllowed(['POST'], 'You may only POST to this URL.')

    def comments_disabled(self):
        jinja = self.rc().get(Jinja2FrontendViewProvider)
        return jinja.render_response('frontend/comments/disabled.html', {})

    def entry_doesnot_exist(self):
        raise NotFound()

    def invalid_csrf_token(self, request, c):
        return self.common(request, c, 'CSRF')

    def invalid_data(self, request, c):
        return self.common(request, c, 'DATA')

    def common(self, request, c, message):
        referer_l = filter(lambda x: x[0] == 'Referer', request.headers)
        qs = {}
        qs['name']    = c.name
        qs['email']   = c.email
        qs['url']     = c.url
        qs['comment'] = c.content
        qs['message'] = message
        if len(referer_l) > 0:
            referer_url = referer_l[-1][1]
        else:
            rc             = self.rc()
            permalink_func = rc.get(EntryPermalinkProvider).authoritative
            referer_url    = permalink_func(c.entry_pkey[1], c.entry_pkey[0])
        parts = tuple(urlparse.urlparse(referer_url))
        _qs = urlparse.parse_qs(parts[4])
        _qs.update(qs)
        s = urllib.urlencode(_qs)
        newparts = (parts[0], parts[1], parts[2], parts[3], s, parts[5])
        return redirect(urlparse.urlunparse(newparts), code=302)

    def storage_error(self):
        raise InternalServerError()

    def unique_error(self, comment):
        return self.success(comment)

    def success(self, c):
        rc             = self.rc()
        permalink_func = rc.get(EntryPermalinkProvider).authoritative
        permalink      = permalink_func(c.entry_pkey[1], c.entry_pkey[0])
        return redirect(permalink, code=302)
