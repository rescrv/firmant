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
        loader = FileSystemLoader(self.settings['JINJA2_TEMPLATE_DIR'])
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


class Jinja2SingleEntry(EntryWriter, Jinja2Base):

    def write(self):
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


class Jinja2ArchiveYearsEntry(EntryWriter, Jinja2Base):

    def write(self):
        env = self.environment

        if not self.write_preconditions(): return

        years = EntryWriter.split_years(self.entries)
        mapr = self.template_mapper
        for year, entries in years:
            year = str(year)
            tmpl = env.get_template(mapr.entry_year(year))
            data = tmpl.render({'entries': entries, 'year': year})
            path = os.path.join(self.settings['OUTPUT_DIR'], year, 'index.html')
            self.log.info(_('processing year archive: %s') % path)
            self.save_to_disk(path, data)
