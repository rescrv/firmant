.. time:: 180424
.. timezone:: America/New_York
.. tag:: code
.. tag:: python
.. tag:: rcos
.. tag:: firmant
.. updated:: 2009-02-17 113130
.. author:: Robert Escriva

.. rights::

    This document is licensed under a 3-clause BSD license.

.. nodefaultfeed::
.. feed:: RCOS

A rework of Firmant for RCOS
============================

So I'm reworking Firmant for RCOS.  This document describes some of the new
features.

For instance, code may be embedded directly into documents like this::

    import hashlib
    import sys
    
    s = hashlib.new('sha1')
    
    s.update(sys.argv[1] + '\n')
    print s.hexdigest()

Tags
----

This document itself has some interesting attributes.  For instance, it is
tagged with: ``code``, ``python``, ``rcos``, and ``firmant``.  If any of those
tags have a feed, the post will be automatically included in the feed.
Additionally, I overrride the default author setting to indicate that it is
myself.  Only ``rcos`` provides a feed.

Feeds
-----

The ``nodefaultfeed`` construct prevents Firmant from putting this post into
catchall feeds.  That is, feeds that implicitly include all entries will not
include this post.
