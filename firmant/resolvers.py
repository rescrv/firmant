import re


class Resolver(object):

    def __init__(self):
        raise NotImplementedError("Subclass, not instantiate Resolver.")

    def resolve(self, request):
        pass


class DateResolver(object):

    year = r'(?P<year>\d{4})/$'
    month = year[:-2] + r'/(?P<month>\d{2})/$'
    day = month[:-2] + r'/(?P<day>\d{2})/$'
    single = day[:-2] + r'/(?P<slug>[-_a-zA-Z0-9]{1,96})/$'

    def __init__(self, prefix=''):
        prefix = r'^/' + prefix
        if prefix != '^/':
            prefix += '/'
        self.recent_re = re.compile(prefix + '$')
        self.year_re = re.compile(prefix + self.year)
        self.month_re = re.compile(prefix + self.month)
        self.day_re = re.compile(prefix + self.day)
        self.single_re = re.compile(prefix + self.single)

    def resolve(self, request):
        match = self.recent_re.match(request.url)
        if match != None:
            return self._recent(request, **match.groupdict())
        match = self.year_re.match(request.url)
        if match != None:
            return self._year(request, **match.groupdict())
        match = self.month_re.match(request.url)
        if match != None:
            return self._month(request, **match.groupdict())
        match = self.day_re.match(request.url)
        if match != None:
            return self._day(request, **match.groupdict())
        match = self.single_re.match(request.url)
        if match != None:
            return self._single(request, **match.groupdict())

    def _recent(self, request):
        return 'RECENT'

    def _year(self, request, year):
        return '%s' % year

    def _month(self, request, year, month):
        return '%s-%s' % (year, month)

    def _day(self, request, year, month, day):
        return '%s-%s-%s' % (year, month, day)

    def _single(self, request, slug, year, month, day):
        return '%s-%s-%s %s' % (year, month, day, slug)
