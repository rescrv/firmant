import datetime
import time
import re

try:
    import json # pragma: no cover
except ImportError: # pragma: no cover
    import simplejson as json

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
    frmt_str = '%Y-%m-%dT%H:%M:%S'
    timestamp = dt.strftime(frmt_str)
    timezone  = dt.strftime('%z')
    if timezone != '':
        return timestamp + timezone[:-2] + ':' + timezone[-2:]
    else:
        return timestamp + 'Z'


def valid_date(year, month, day):
    try:
        year = int(year)
    except ValueError:
        raise ValueError('invalid value for year; cannot cast to int')
    try:
        month = int(month)
    except ValueError:
        raise ValueError('invalid value for month; cannot cast to int')
    try:
        day = int(day)
    except ValueError:
        raise ValueError('invalid value for day; cannot cast to int')
    try:
        dt = datetime.date(year, month, day)
    except ValueError:
        raise
    return (dt.year, dt.month, dt.day)


if hasattr(datetime.datetime, 'strptime'):
    strptime = datetime.datetime.strptime
else:
    def strptime(date_string, format): # pragma: no cover
        struct_time = time.strptime(date_string, format)
        return datetime.datetime(*struct_time[0:6])

def uniq(l):
    l.sort()
    return uniq_presorted(l)

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

def sha1(text):
    try:
        import hashlib
        s = hashlib.new('sha1')
    except ImportError: # pragma: no cover
        import sha
        s = sha.new()
    s.update(text)
    return s.hexdigest()


# While it most certainly is not perfect, this regular expression makes sure
# users at least attempt to form a valid email.  An invalid email is not
# necessarily indicative of spammers, but of users of software that does not
# conform to RFCs.
email_re = re.compile('^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$')
