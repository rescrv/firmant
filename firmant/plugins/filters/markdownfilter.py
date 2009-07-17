import markdown


class MarkdownFilter(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def filter(self, slot, content):
        if self.settings['MARKDOWN_XHTML_SAFE_MODE'] != None:
            return markdown.markdown(text=content,
            safe_mode=self.settings['MARKDOWN_XHTML_SAFE_MODE'])
        return markdown.markdown(text=content)

    def provides(self, slot):
        if slot == 'XHTML' and self.settings['MARKDOWN_XHTML_ENABLED']:
            return True
        return False
