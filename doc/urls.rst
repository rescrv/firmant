.. _customizing_urls:

Customizing URLs
================

Firmant provides a means to customize the URLs of all generated content.
Content writers provide a set of attributes which identify each output file by a
set of key-value pairs (a Python dictionary).  User-provided URL rules specify
how to create URLs from the attributes.  A rule is said to match a set of
attributes when the set of keys of the rule are the same as the set of keys of
the attributes.  A simple example illustrates how rules work.  The following
rule defines a URL which corresponds to a post in a typical blog.

   html {'type': 'post'} /{year:04}/{month:02}/{day:02}/{slug}

Later we will show how Firmant uses this rule to construct the URLs in a web
blog.  For now, lets break down the URL rule into its three components:

File extension:
   The file extension will be appended to all files, and allows the web server
   to serve the file with the correct mimetype.

Fixed attributes:
   The fixed attributes are key-value pairs which are constant.  A set of
   attributes may only match the URL rule if all fixed attributes of the URL
   rule are present in the set.

Format string:
   The format string of the URL rule specifies how to compose the set of
   attributes to create a final URL.  This string must conform to PEP
   :pep:`3101` with the additional restriction that all replacement fields have
   a field name specified.

To construct a URL for a set of attributes, Firmant finds the first rule whose
attributes have the same values as the set of attributes for which we are
constructing the rule.  Fixed attributes must share the same value.  For
instance, the rule shown above will match the attributes ``{'type': 'post',
'year': 2011, 'month': 5, 'day': 19, 'slug': 'hithere'}``, but would not match
``{'year': 2011, 'month': 5, 'day': 19, 'slug': 'hithere'}`` or ``{'type':
'notpost', 'year': 2011, 'month': 5, 'day': 19, 'slug': 'hithere'}``.

Each writer object expects a certain set of URL rules.  Most packages provide a
default set of URL rules which satisfy the writers within the package.  Users
may then override the URL rules in the file specified by XXX.

.. todo::

   Describe how to override URL rules through the config system.
