from docutils import core


class RestructuredTextFilter(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def filter(self, slot, content):
        parts = core.publish_parts(source=content, writer_name='html')
        return parts['fragment']

    def provides(self, slot):
        return slot == 'XHTML' \
               and self.settings['RESTRUCTUREDTEXT_XHTML_ENABLED']
