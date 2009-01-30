__all__ = ['settings']


class Settings(object):

    def __init__(self):
        self._settings = None

    def configure(self, settings_module):
        if self._settings != None:
            raise ImportError('Settings already configured.')

        try:
            settings = __import__(settings_module, {}, {}, [''])
        except ImportError:
            raise ImportError('Settings import failed')

        self._settings = {}
        for setting in dir(settings):
            if setting.upper() == setting:
                value = getattr(settings, setting)
                self._settings[setting] = value

    def reconfigure(self, settings_module):
        self.reset()
        self.configure(settings_module)

    def reset(self):
        self._settings = None

    def __getitem__(self, item):
        return self._settings[item]

    def iteritems(self):
        return self._settings.iteritems()


# This is the global settings for the application.  It is a Settings class, but
# that is just a loose subclass of a dictionary.
settings = Settings()
