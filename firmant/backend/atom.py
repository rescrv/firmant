from firmant.backend import get_entry_class, get_feed_class, get_slug_re
from firmant.utils import ProxyObject

Entry = ProxyObject(get_entry_class)
Feed = ProxyObject(get_feed_class)
slug_re = ProxyObject(get_slug_re)
