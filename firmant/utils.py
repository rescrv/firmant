def get_module(plugin):
    try:
        modules = plugin.split('.')
        mod = __import__(plugin, {}, {}, [])
        for module in modules[1:]:
            mod = getattr(mod, module)
        return mod
    except ImportError:
        raise


class ProxyObject(object):

    def __init__(self, obj):
        super(ProxyObject, self).__init__()
        # first set the list of 'local' attrs for __setattr__
        self.__dict__['_local'] = ('_local', '_object' )
        self._object = obj

    def __setattr__(self, attr, value):
        # Case 1: attr is in _local.
        if attr in self.__dict__['_local']:
            self.__dict__[attr] = value
        # Case 2: attr is in _proxied.
        else:
            setattr(self.__dict__['_object'], attr, value)

    def __getattr__(self, attr):
        attribute = getattr(self.__dict__['_object'], attr)
        # Case 1: attr is a method.
        if callable(attribute):
            import types
            def method(*args, **kwargs):
                if attribute is types.MethodType:
                    args = (self.__dict__['_object'],) + args
                return attribute(*args, **kwargs)
            return method
        # Case 2: attr is an attribute.
        else:
            return attribute
        # Default: raise AttributeError.
        raise AttributeError()

    def __delattr__(self, attr):
        # Case 1: attr is in _local (raise AttributeError).
        if attr in self.__dict__['_local']:
            raise AttributeError()
        # Case 2: attr is in _proxied.
        else:
            del self.__dict__['_object'].__dict__[attr]
