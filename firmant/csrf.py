# Cross-site-request-forgery protection module.
# This implements an interface for managing tokens in forms.  These tokens help
# protect against csrf.

from firmant.plugins import SingleProviderPlugin


class CSRFTokenProvider(SingleProviderPlugin):

    provider_setting = 'CSRF_TOKEN_PROVIDER'

    def request_token(self, ip_addr):
        return self._provider.request_token(ip_addr)

    def consume_token(self, token, ip_addr):
        return self._provider.consume_token(token, ip_addr)
