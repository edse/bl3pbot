import hmac
import urllib
import base64
import hashlib
import requests
from django.conf import settings
from .base import *  # noqa


class Bl3p(object):

    def get_balance(self):
        return self.call(settings.EXCHANGES['BL3P']['private']['paths']['get_balance'], {})

    def add_order(self, params):
        return self.call(settings.EXCHANGES['BL3P']['private']['paths']['add_order'], params)

    def get_order(self, params):
        return self.call(settings.EXCHANGES['BL3P']['private']['paths']['get_order'], params)

    def get_headers(self, path, params):
        post_data = urllib.parse.urlencode(params)
        body = '%s%c%s' % (path, 0x00, post_data)
        headers = {
            'Rest-Key': settings.EXCHANGES['BL3P']['private']['public_key'],
            'Rest-Sign': self.get_signature(body),
        }
        return headers

    def get_signature(self, body):
        return base64.b64encode(
            hmac.new(
                base64.b64decode(
                    settings.EXCHANGES['BL3P']['private']['private_key']
                ),
                body.encode('utf-8'),
                hashlib.sha512
            ).digest()
        )

    def execute(self, path, params, headers, soft_run):
        if soft_run:
            logger.log('soft_run', 'Skiping real api call: {}'.format(path))
            return None

        response = requests.post(path, data=params, headers=headers)
        if response.status_code != 200:
            logger.log('error', 'unexpected response: {}'.format(response.content))
            return None

        return response.json()

    def call(self, path, params):
        fullpath = settings.EXCHANGES['BL3P']['private']['url'] + path
        headers = self.get_headers(path, params)

        # execute call
        return self.execute(
            path=fullpath,
            params=params,
            headers=headers,
            soft_run=settings.EXCHANGES['BL3P']['soft_run']
        )
