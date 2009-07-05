from werkzeug import Local
from werkzeug import LocalManager
import datetime
import time

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

if hasattr(datetime.datetime, 'strptime'):
    strptime = datetime.datetime.strptime
else:
    def strptime(date_string, format):
        struct_time = time.strptime(date_string, format)
        return datetime.datetime(*struct_time[0:6])

def uniq(l):
    l.sort()
    uniq_presorted(l)

def uniq_presorted(l):
    if (len(l) > 0):
        ret = []
        ret.append(l[0])
        for i in range(1, len(l)):
            if l[i] != l[i - 1]:
                ret.append(l[i])
        return ret
    else:
        return []

local = Local()
local_manager = LocalManager([local])
