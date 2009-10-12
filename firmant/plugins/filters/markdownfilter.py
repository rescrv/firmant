import markdown


class MarkdownFilter(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def filter(self, slot, content):
        args = dict()
        args['text'] = content

        if self.settings['MARKDOWN_XHTML_SAFE_MODE'] != None:
            args['safe_mode'] = self.settings['MARKDOWN_XHTML_SAFE_MODE']

        if isinstance(self.settings.get('MARKDOWN_EXTENSIONS', None), list):
            args['extensions'] = self.settings['MARKDOWN_EXTENSIONS']

        return markdown.markdown(**args)

    def provides(self, slot):
        if slot == 'XHTML' and self.settings['MARKDOWN_XHTML_ENABLED']:
            return True
        return False
