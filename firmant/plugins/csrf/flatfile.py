import datetime
import os
import socket
import re

from firmant.utils import sha1
from firmant.utils import strptime


token_re = re.compile(r'(\d{14})-[0-9a-z]{40}-(.+)')
date_format = '%Y%m%d%H%M%S'


class FlatfileCSRFTokenProvider(object):

    def __init__(self, rc, settings):
        self.settings = settings

    def request_token(self, ip_addr):
        try:
            socket.inet_pton(socket.AF_INET, ip_addr)
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip_addr)
            except socket.error:
                raise ValueError('Invalid IP address')
        now    = datetime.datetime.now().strftime(date_format)
        # 64 bits provides sufficient randomness to protect against any
        # practical brute-force attack.
        salt   = os.urandom(8)
        secret = self.settings['CSRF_SERVER_SECRET']
        # Put secret second to prevent attacks where first few blocks are
        # cached.
        hash   = sha1(salt + secret)
        token  = '%s-%s-%s' % (now, hash, ip_addr)
        path   = os.path.join(self.settings['CSRF_TOKENS_DIR'], token)
        os.mkdir(path, 0400)
        return token

    def consume_token(self, token, ip_addr):
        match  = token_re.match(token)
        if match is None:
            return False
        groups = match.groups()
        dt     = strptime(groups[0], date_format)
        ip     = groups[1]
        path   = os.path.join(self.settings['CSRF_TOKENS_DIR'], token)
        ttl    = datetime.timedelta(seconds=self.settings['CSRF_TOKEN_TTL'])
        if dt + ttl >= datetime.datetime.now() and os.path.isdir(path):
            os.rmdir(path)
            return ip == ip_addr
        return False
