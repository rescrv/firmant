from werkzeug import Local
from werkzeug import LocalManager

def not_implemented(*args, **kwargs):
    raise NotImplementedError("This function is not implemented")


def get_module(plugin):
    try:
        modules = plugin.split('.')
        mod = __import__(plugin, {}, {}, [])
        for module in modules[1:]:
            mod = getattr(mod, module)
        return mod
    except ImportError:
        raise


def mod_to_dict(module):
    dictionary = {}
    for attr in dir(module):
        if attr.upper() == attr:
            value = getattr(module, attr)
            dictionary[attr] = value
    return dictionary


def RFC3339(dt):
    frmt_str = '%Y-%m-%dT%H:%M:%S%z'
    ret = dt.strftime(frmt_str)
    return ret[:-2] + ':' + ret[-2:]

local = Local()
local_manager = LocalManager([local])
