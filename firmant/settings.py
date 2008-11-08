class Settings(dict):

    def __init__(self, settings_module):
        super(Settings, self).__init__()
        try:
            settings = __import__(settings_module, {}, {}, [''])
        except ImportError:
            raise ImportError('Settings import failed')

        for setting in dir(settings):
            if setting.upper() == setting:
                value = getattr(settings, setting)
                self[setting] = value
