import datetime
from werkzeug import Response
from werkzeug.routing import Rule, \
                             Submount

from firmant.csrf import CSRFTokenProvider
from firmant.datasource.atom import AtomProvider
from firmant.datasource.comments import Comment
from firmant.datasource.comments import CommentProvider


class CommentDataGlobalProvider(object):

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    def globals_dict(self):
        def comment_post_url(published, slug):
            endpoint = __name__ + '.CommentSubmissionHandler.post'
            values = {}
            values['year']  = published.year
            values['month'] = published.month
            values['day']   = published.day
            values['slug']  = slug

            urls = self.rc().get('urls')
            return urls.build(endpoint, values, force_external=True)
        return {'comment_post_url': comment_post_url}


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
            return self.invalid_data()
        if c.name == '' or \
            c.email == '' or \
            c.url == '' or \
            c.content == '':
            return self.invalid_data()

        # Check for valid csrf token.
        csrf_token = request.form.get('csrf_token', '')
        ip_addr    = request.remote_addr
        if not rc.get(CSRFTokenProvider).consume_token(csrf_token, ip_addr):
            return self.invalid_csrf_token()

        # Store comment object
        comment_provider = rc.get(CommentProvider)
        try:
            comment_provider.save(c)
        except CommentProvider.UniqueViolationError:
            return self.unique_error()
        except CommentProvider.StorageError:
            return self.storage_error()

        return self.success()

    def method_not_allowed(self):
        return Response('Method not allowed.', mimetype='text/plain')

    def comments_disabled(self):
        return Response('Submission of comments is disabled.', mimetype='text/plain')

    def entry_doesnot_exist(self):
        return Response('Entry does not exist.', mimetype='text/plain')

    def invalid_csrf_token(self):
        return Response('Invalid CSRF Token.', mimetype='text/plain')

    def invalid_data(self):
        return Response("Something didn't validate.", mimetype='text/plain')

    def storage_error(self):
        return Response("Storage error storing comment.", mimetype='text/plain')

    def unique_error(self):
        return Response("Comment already saved.", mimetype='text/plain')

    def success(self):
        return Response('IT WORKED', mimetype='text/plain')
