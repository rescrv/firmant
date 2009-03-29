import markdown

from firmant.configuration import settings
from firmant.filters import register


class MarkdownFilter:

    def __init__(self, safe_mode=None):
        self._safe_mode = safe_mode

    def filter(self, content):
        if self._safe_mode != None:
            return markdown.markdown(text=content, safe_mode=self._safe_mode)
        return markdown.markdown(text=content)


def load():
    if settings['MARKDOWN_XHTML_ENABLED']:
        mf = MarkdownFilter(settings['MARKDOWN_XHTML_SAFE_MODE'])
        register('XHTML', mf)
