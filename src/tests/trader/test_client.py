from django.conf import settings
from tests.base import BaseTestCase
from trader.client import Bl3p


class TestBl3pClient(BaseTestCase):

    def test_soft_run(self):
        settings.EXCHANGES['BL3P']['soft_run'] = True

        result = Bl3p().get_balance()
        assert result is None

        result = Bl3p().get_order({}, 'BTCEUR')
        assert result is None

        result = Bl3p().add_order({}, 'BTCEUR')
        assert result is None

        settings.EXCHANGES['BL3P']['soft_run'] = False

    def test_get_balance(self):
        result = Bl3p().get_balance()

        assert result['result'] == 'success'

        assert result['data']['trade_fee'] > 0
        assert result['data']['user_id'] > 0

        assert 'EUR' in result['data']['wallets']
        assert 'available' in result['data']['wallets']['EUR']
        assert 'balance' in result['data']['wallets']['EUR']

        assert 'LTC' in result['data']['wallets']
        assert 'available' in result['data']['wallets']['LTC']
        assert 'balance' in result['data']['wallets']['LTC']

        assert 'BTC' in result['data']['wallets']
        assert 'available' in result['data']['wallets']['BTC']
        assert 'balance' in result['data']['wallets']['BTC']

    def test_get_order(self):
        params = {'order_id': 21703522}
        result = Bl3p().get_order(params, 'BTCEUR')

        assert result['result'] == 'success'
        assert result['data']['date'] > 0
        assert result['data']['currency'] == 'EUR'
        assert result['data']['status'] == 'closed'
        assert result['data']['order_id'] == params['order_id']
        assert result['data']['type'] == 'bid'

        assert 'price' in result['data']

        assert 'currency' in result['data']['price']
        assert 'value_int' in result['data']['price']
        assert 'value' in result['data']['price']
        assert 'display_short' in result['data']['price']
        assert 'display' in result['data']['price']

    def test_add_order(self):
        pass
