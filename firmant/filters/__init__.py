_filter_dict = {}

def register(slot, filter, force=False):
    try:
        _filter_dict[slot]
    except KeyError:
        pass
    else:
        if not force:
            raise RuntimeError("Slot '%s' already registered" % slot)
    _filter_dict[slot] = filter

def text_filter(slot, content):
    try:
        _filter_dict[slot]
    except KeyError:
        raise RuntimeError("Slot '%s' not registered" % slot)
    return _filter_dict[slot].filter(content)
