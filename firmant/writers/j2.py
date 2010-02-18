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
from firmant.writers import Writer
from firmant import utils


class Jinja2Base(Writer):

    @property
    def environment(self):
        loader = FileSystemLoader(self.settings['JINJA2_TEMPLATE_DIR'])
        env = Environment(loader=loader)
        return env


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


class Jinja2SingleEntry(Jinja2Base):

    def write(self):
        env = self.environment

        if not self.write_preconditions(): return

        for entry in self.entries:
            # Hackish, but works around the python strftime bug.
            dt = entry.published.date()
            path = '%04i/%02i/%02i/%s' % \
                    (dt.year, dt.month, dt.day, entry.slug)
            self.log.info(_('processing post: %s') % path)

            default = Jinja2TemplateMapper(self.settings)
            template_mapper = self.settings.get('TEMPLATE_MAPPER', default)

            tmp  = env.get_template(template_mapper.single_entry(entry))
            data = tmp.render({'entry': entry})

            try:
                utils.safe_mkdir(path)
            except OSError:
                raise
                self.log.error(_('cannot create dir: %s') % path)
                continue

            try:
                f = open(os.path.join(path, 'index.html'), 'w+')
            except IOError:
                self.log.error(_('cannot open file: %s') % path)
                continue
            f.write(data.encode('utf-8'))
            f.close()
