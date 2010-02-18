# Copyright (c) 2010, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Firmant nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

from firmant.i18n import _
from firmant.writers import EntryWriter
from firmant.writers import Writer
from firmant import utils


class Jinja2Base(Writer):

    @property
    def environment(self):
        loader = FileSystemLoader(self.settings['TEMPLATE_DIR'])
        env = Environment(loader=loader)
        return env

    @property
    def template_mapper(self):
        '''Return the a class for mapping entries/feeds/tags to templates.
        '''
        default = Jinja2TemplateMapper(self.settings)
        return self.settings.get('TEMPLATE_MAPPER', default)

    def save_to_disk(self, path, data):
        '''Save the data to ``path`` on disk.

        :func:`firmant.utils.safe_mkdir` will be called on the
        :func:`os.path.dirname` of ``path``.
        '''
        try:
            utils.safe_mkdir(os.path.dirname(path))
        except OSError:
            raise
            self.log.error(_('cannot create dir: %s') % path)
            return False
        try:
            f = open(path, 'w+')
        except IOError:
            self.log.error(_('cannot open file: %s') % path)
            return False
        f.write(data.encode('utf-8'))
        f.close()
        return True


class Jinja2TemplateMapper(object):
    '''Class to map entries to templates.

    Eventually it will be possible to have per-entry templates override the
    defaults.
    '''

    def __init__(self, settings):
        self.settings = settings

    def single_entry(self, entry):
        '''Call this to get the template that corresponds to ``entry``.
        '''
        return 'entries/single.html'

    def entry_year(self, year):
        '''Call this to get the template that corresponds to ``year``.

        ``year`` should be a string representing the year.
        '''
        return 'entries/year.html'

    def entry_month(self, year, month):
        '''Call this to get the template that corresponds to ``year`` and
        ``month``.

        ``year`` and ``month`` should both be a string representing a particular
        month.
        '''
        return 'entries/month.html'

    def entry_day(self, year, month, day):
        '''Call this to get the template that corresponds to ``year``,
        ``month``, and ``day``.

        ``year``, ``month``, ``day`` should all be strings representing a
        particular day.
        '''
        return 'entries/day.html'


class Jinja2SingleEntry(EntryWriter, Jinja2Base):
    '''Write full entries out to their appropriate files.
    '''

    def path(self, entry):
        '''Return the path for the entry.
        '''
        # Hackish, but works around the python strftime bug.
        dt = entry.published.date()
        return '%04i/%02i/%02i/%s' % (dt.year, dt.month, dt.day, entry.slug)

    def log_processing(self, entry):
        '''Log to the info logger that we are processing entries.
        '''
        self.log.info(_('processing post: %s') % self.path(entry))

    def write(self):
        r'''Write the entries to the filesystem individually.

        Example:

            >>> j2se = Jinja2SingleEntry(settings, blog)
            >>> j2se.log = Mock('log')
            >>> j2se.write()
            Called log.info(u'processing post: 2009/12/31/party')
            Called log.info(u'processing post: 2010/01/01/newyear')
            Called log.info(u'processing post: 2010/02/01/newmonth')
            Called log.info(u'processing post: 2010/02/02/newday')
            Called log.info(u'processing post: 2010/02/02/newday2')
            >>> cat(os.path.join(settings['OUTPUT_DIR'],
            ... '2010/02/02/newday/index.html'))
            Called stdout.write('newday\n')
            Called stdout.write('2010-02-02 00:10:00\n')
            Called stdout.write('John Doe\n')
            Called stdout.write('baz foo \n')
            Called stdout.write('default baz foo \n')
            Called stdout.write('Same as source.\n')
            Called stdout.write('2010-02-02 00:10:00\n')
            Called stdout.write('Here Is a New Day!\n')
            Called stdout.write('<p>This is the content of the new day.</p>\n')
            Called stdout.write('US/Eastern')

        '''
        env = self.environment

        if not self.write_preconditions(): return

        for entry in self.entries:
            self.log_processing(entry)
            path = os.path.join(self.settings['OUTPUT_DIR'], self.path(entry))
            path = os.path.join(path, 'index.html')
            mapr = self.template_mapper
            tmpl = env.get_template(mapr.single_entry(entry))
            data = tmpl.render({'entry': entry})
            self.save_to_disk(path, data)


class Jinja2EntryArchive(EntryWriter, Jinja2Base):
    '''Group entries in a generic fashion.

    Yearly, monthly, and daily views should all derive from this class.
    '''

    def write(self):
        env = self.environment

        if not self.write_preconditions(): return

        keyed_entries = self.group_entries()
        mapr = self.template_mapper
        for key, entries in keyed_entries:
            entries.sort(key=lambda e: (e.published.date(), e.slug))
            path = self.path(key)
            template = self.get_template(key, entries)
            context  = self.get_context(key, entries)
            data = template.render(context)
            self.log.info(self.info % path)
            path = os.path.join(self.settings['OUTPUT_DIR'], path, 'index.html')
            self.save_to_disk(path, data)


class Jinja2EntryArchiveYearly(Jinja2EntryArchive):
    r'''Write the entries to the filesystem in lists grouped by year.

    Example:

        >>> j2eay = Jinja2EntryArchiveYearly(settings, blog)
        >>> j2eay.log = Mock('log')
        >>> j2eay.write()
        Called log.info('processing yearly archive: 2009')
        Called log.info('processing yearly archive: 2010')
        >>> cat(os.path.join(settings['OUTPUT_DIR'], '2010/index.html'))
        Called stdout.write('2010\n')
        Called stdout.write('2010-01-01-newyear\n')
        Called stdout.write('2010-02-01-newmonth\n')
        Called stdout.write('2010-02-02-newday\n')
        Called stdout.write('2010-02-02-newday2\n')

    '''

    def group_entries(self):
        return self.split_years(self.entries)

    def path(self, key):
        return '%04i' % key

    def get_template(self, key, entries):
        mapr = self.template_mapper
        return self.environment.get_template(mapr.entry_year(key))

    def get_context(self, key, entries):
        return {'entries': entries, 'year': '%04i' % key}

    info = _('processing yearly archive: %s')


class Jinja2ArchiveMonthsEntry(EntryWriter, Jinja2Base):
    '''Create lists of entries grouped by month.
    '''

    def write(self):
        r'''Write the entries to the filesystem in lists grouped by month.

        Example:

            >>> j2ame = Jinja2ArchiveMonthsEntry(settings, blog)
            >>> j2ame.log = Mock('log')
            >>> j2ame.write()
            Called log.info('processing monthly archive: 2009/12')
            Called log.info('processing monthly archive: 2010/01')
            Called log.info('processing monthly archive: 2010/02')
            >>> cat(os.path.join(settings['OUTPUT_DIR'], '2010/02/index.html'))
            Called stdout.write('2010-02\n')
            Called stdout.write('2010-02-01-newmonth\n')
            Called stdout.write('2010-02-02-newday\n')
            Called stdout.write('2010-02-02-newday2\n')

        '''
        env = self.environment

        if not self.write_preconditions(): return

        months = EntryWriter.split_months(self.entries)
        mapr = self.template_mapper
        for (year, month), entries in months:
            entries.sort(key=lambda e: (e.published.date(), e.slug))
            path = '%04i/%02i' % (year, month)
            year = '%04i' % year
            month = '%02i' % month
            tmpl = env.get_template(mapr.entry_month(year, month))
            data = tmpl.render({'entries': entries, 'year': year,
                'month': month})
            self.log.info(_('processing monthly archive: %s') % path)
            path = os.path.join(self.settings['OUTPUT_DIR'], path, 'index.html')
            self.save_to_disk(path, data)


class Jinja2ArchiveDaysEntry(EntryWriter, Jinja2Base):
    '''Create lists of entries for given days.
    '''

    def write(self):
        r'''Write the entries to the filesystem in lists grouped by day.

        Example:

            >>> j2ade = Jinja2ArchiveDaysEntry(settings, blog)
            >>> j2ade.log = Mock('log')
            >>> j2ade.write()
            Called log.info('processing daily archive: 2009/12/31')
            Called log.info('processing daily archive: 2010/01/01')
            Called log.info('processing daily archive: 2010/02/01')
            Called log.info('processing daily archive: 2010/02/02')
            >>> cat(os.path.join(settings['OUTPUT_DIR'], '2010/02/02/index.html'))
            Called stdout.write('2010-02-02\n')
            Called stdout.write('2010-02-02-newday\n')
            Called stdout.write('2010-02-02-newday2\n')

        '''
        env = self.environment

        if not self.write_preconditions(): return

        days = EntryWriter.split_days(self.entries)
        mapr = self.template_mapper
        for (year, month, day), entries in days:
            entries.sort(key=lambda e: (e.published.date(), e.slug))
            path = '%04i/%02i/%02i' % (year, month, day)
            year = '%04i' % year
            month = '%02i' % month
            day = '%02i' % day
            tmpl = env.get_template(mapr.entry_day(year, month, day))
            data = tmpl.render({'entries': entries, 'year': year,
                'month': month, 'day': day})
            self.log.info(_('processing daily archive: %s') % path)
            path = os.path.join(self.settings['OUTPUT_DIR'], path, 'index.html')
            self.save_to_disk(path, data)


def _setUp(test):
    '''Setup the Jinja2 test cases.
    '''
    import tempfile

    from minimock import Mock

    from firmant.parser import Blog
    from firmant.utils import cat

    settings = {}
    settings['OUTPUT_DIR'] = tempfile.mkdtemp()
    settings['TEMPLATE_DIR'] = 'testdata/pristine/templates'
    test.globs['settings'] = settings
    test.globs['blog']     = Blog('testdata/pristine/')
    test.globs['Mock']     = Mock
    test.globs['cat']      = lambda out: cat(out, Mock('stdout'))


def _tearDown(test):
    '''Cleanup the Jinja2 test cases.
    '''
    import shutil
    shutil.rmtree(test.globs['settings']['OUTPUT_DIR'])
