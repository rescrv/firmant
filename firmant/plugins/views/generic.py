import datetime

from firmant.datasource.atom import AtomProvider
from firmant.datasource.atom import slug_re
from firmant.utils import valid_date
from firmant.utils import force_to_int


def paginate(rc, limit, func, page):
    offset = page * limit
    objects, count_remain = func(limit, offset)

    p = Page()
    p.has_older = count_remain > 0
    p.has_newer = offset > 0

    rc           = rc()
    urls         = rc.get('urls')
    endpoint     = rc.get('endpoint')
    args         = rc.get('args').copy()

    if p.has_newer:
        if page == 1:
            # We have this exception so that we don't use ?page=0
            p.newer = urls.build(endpoint, args, force_external=True)
        else:
            n_args = args.copy()
            n_args['page'] = page - 1
            p.newer = urls.build(endpoint, n_args, force_external=True)
    else:
        p.newer = None

    if p.has_older:
        n_args = args.copy()
        n_args['page'] = page + 1
        p.older = urls.build(endpoint, n_args, force_external=True)
    else:
        p.older = None

    return objects, p


class Page(object):

    __slots__ = ['has_older', 'has_newer', 'newer', 'older']


class GenericEntryViewProvider(object):
    '''Subclass this and override the ``render'' method.
    For each type you get either a list of entries, or a single entry; and a
    Page object.  Subclass this and override methods to make it useful.'''

    def __init__(self, rc, settings):
        self.rc       = rc
        self.settings = settings

    @property
    def rules(self):
        name = __name__ + '.GenericEntryViewProvider.'
        url_rules = [
            Rule('/', endpoint=name + 'recent'),
            Rule('/<int(fixed_digits=4):year>/', endpoint=name + 'year'),
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>/',
                 endpoint=name + 'month'),
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>' + \
                 '/<int(fixed_digits=2):day>/', endpoint=name + 'day'),
            Rule('/<int(fixed_digits=4):year>/<int(fixed_digits=2):month>' + \
                 '/<int(fixed_digits=2):day>/<slug>', endpoint=name + 'single')
        ]
        if self.prefix != '':
            return [Submount('/' + self.prefix, url_rules)]
        else:
            return url_rules

    def common(self, request, func, year=1, month=1, day=1):
        try:
            year, month, day = valid_date(year, month, day)
        except ValueError:
            return self.invalid_args(request)
        page = force_to_int(request.args.get('page', 0), 0)
        rc = self.rc()
        ap = rc.get(AtomProvider)
        paginate_func = func(ap, year, month, day)
        entries, page = paginate(lambda: rc, self.limit, paginate_func, page)
        return entries, page

    def recent(self, request):
        def func(ap, y, m, d):
            return lambda l, o: ap.entry.recent(l, o)
        entries, page = self.common(request, func)
        return self._recent(request, entries, page)

    def year(self, request, year):
        def func(ap, y, m, d):
            return lambda l, o: ap.entry.year(y, l, o)
        entries, page = self.common(request, func, year)
        return self._year(request, entries, page, year)

    def month(self, request, year, month):
        def func(ap, y, m, d):
            return lambda l, o: ap.entry.month(y, m, l, o)
        entries, page = self.common(request, func, year, month)
        return self._month(request, entries, page, year, month)

    def day(self, request, year, month, day):
        def func(ap, y, m, d):
            return lambda l, o: ap.entry.day(y, m, d, l, o)
        entries, page = self.common(request, func, year, month, day)
        return self._day(request, entries, page, year, month, day)

    def single(self, request, slug, year, month, day):
        try:
            year, month, day = valid_date(year, month, day)
        except ValueError:
            return self.invalid_args(request)
        if slug_re.match(slug) == None:
            return self.invalid_args(request)

        rc = self.rc()
        ap = rc.get(AtomProvider)
        entry = ap.entry.single(slug, year, month, day)
        if entry is None:
            raise NotFound('Entry not found.')
        return self._single(request, entry)
