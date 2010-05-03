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


'''Firmant is a framework for developing static web applications.

Much of today's web development focuses on developing dynamic applications that
regenerate the page for each view.  Firmant takes a different approach that
allows for publishing of static content that can be served by most http servers.

Some of the benefits of this approach include:

 * Build locally, deploy anywhere.  Many notable server distributions (including
   CentOS 5, and Debian Lenny) still ship old (pre-2.6) versions of Python.
   With Firmant, this is not an issue as static output may be published anywhere
   independent of the system where it was built.
 * Quicker page load times.  Search engines and viewers expect near-instant page
   load times and static content can meet these expectations.  Dynamic content
   can as well; however, it often requires more than simple hardware to do so.
 * Offline publishing capability.  Previewing changes to a website does not
   require Internet access, as the changes are all made locally.  Changes do not
   need to be pushed to a remote server.
 * Store content in revision control.  This is not strictly a feature granted by
   generating static pages.  Firmant is designed to make storing all content in
   a repository a trivial task -- something that web application frameworks that
   are powered by relational databases do not consider.

Modules in this package:

.. autosummary::
   :toctree: generated

   chunks
   du
   paginate
   routing
   utils
   writers

'''
