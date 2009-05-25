import markdown

from firmant.configuration import settings
from firmant.filters import FilterProvider


class MarkdownFilter(FilterProvider):

    @classmethod
    def filter(cls, slot, content):
        if settings['MARKDOWN_XHTML_SAFE_MODE'] != None:
            return markdown.markdown(text=content,
            safe_mode=settings['MARKDOWN_XHTML_SAFE_MODE'])
        return markdown.markdown(text=content)

    @classmethod
    def provides(cls):
        if settings['MARKDOWN_XHTML_ENABLED']:
            return ['XHTML']
        return []
