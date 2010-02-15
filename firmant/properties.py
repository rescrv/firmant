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


def property_regex(attr, name, regex, default=None, doc=None):
    '''Create a property where assigned values much match a regular expression.
    '''
    def getter(self):
        return getattr(self, attr, default)
    def setter(self, val):
        if val is not None:
            val = unicode(val)
        if val is not None and regex.match(val) is None:
            error = "Invalid value for '%s'.  Failed to match regex." % name
            raise ValueError(error)
        if val is None:
            setattr(self, attr, default)
        else:
            setattr(self, attr, val)
    return property(getter, setter, doc=doc)


def property_unicode(attr, name, default=None, doc=None):
    '''Create a property where assigned values are cast to unicode
    '''
    def getter(self):
        return getattr(self, attr, default)
    def setter(self, val):
        if val is None:
            setattr(self, attr, default)
        else:
            setattr(self, attr, unicode(val))
    return property(getter, setter, doc=doc)
