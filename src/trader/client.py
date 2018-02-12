import base64
import hashlib
import hmac
import urllib

import requests
from django.conf import settings
from trader.base import *  # noqa


class Bl3p(object):

    def get_balance(self):
        return self._call(settings.EXCHANGES['BL3P']['private']['paths']['get_balance'], {})

    def add_order(self, params, pair):
        return self._call(
            path=settings.EXCHANGES['BL3P']['private']['paths']['add_order'].format(pair=pair),
            params=params
        )

    def get_order(self, params, pair):
        return self._call(
            path=settings.EXCHANGES['BL3P']['private']['paths']['get_order'].format(pair=pair),
            params=params
        )

    def _get_headers(self, path, params):
        post_data = urllib.parse.urlencode(params)
        body = '%s%c%s' % (path, 0x00, post_data)
        headers = {
            'Rest-Key': settings.EXCHANGES['BL3P']['private']['public_key'],
            'Rest-Sign': self._get_signature(body),
        }
        return headers

    def _get_signature(self, body):
        return base64.b64encode(
            hmac.new(
                base64.b64decode(
                    settings.EXCHANGES['BL3P']['private']['private_key']
                ),
                body.encode('utf-8'),
                hashlib.sha512
            ).digest()
        )

    def _execute(self, path, params, headers, soft_run):
        if soft_run:
            logger.log('soft_run', 'Skiping real api call: {}'.format(path))
            return None

        response = requests.post(path, data=params, headers=headers)
        if response.status_code != 200:
            logger.log('error', 'unexpected response: {}'.format(response.content))
            return None

        return response.json()

    def _call(self, path, params):
        fullpath = settings.EXCHANGES['BL3P']['private']['url'] + path
        headers = self._get_headers(path, params)

        # execute call
        return self._execute(
            path=fullpath,
            params=params,
            headers=headers,
            soft_run=settings.EXCHANGES['BL3P']['soft_run']
        )
