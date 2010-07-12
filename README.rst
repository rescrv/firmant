Firmant is a framework for developing static web applications.

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
