import pytest
from django.conf import settings
from tests.base import BaseTestCase
from trader.trader import Trader
from trader.models import Session
from model_mommy import mommy


@pytest.mark.django_db
class TestTrader(BaseTestCase):

    @pytest.mark.django_db
    def test_get_sell_amount(self):
        session = mommy.make(Session)
        trader = Trader(session_id=session.id)

        amount = trader.get_sell_amount()

        assert amount == 59408221

    @pytest.mark.django_db
    def test_get_sell_max_value(self):
        session = mommy.make(Session)
        trader = Trader(session_id=session.id)

        settings.EXCHANGES['BL3P']['max_sell_value'] = {'LTCEUR': 1, 'BTCEUR': 1}

        amount = trader.get_sell_amount()

        settings.EXCHANGES['BL3P']['max_sell_value'] = {'LTCEUR': -1, 'BTCEUR': -1}

        assert amount == 1

    @pytest.mark.django_db
    def test_get_sell_min_value(self):
        session = mommy.make(Session)
        trader = Trader(session_id=session.id)

        settings.EXCHANGES['BL3P']['min_sell_value'] = {'BTCEUR': 100000000, 'LTCEUR': 100000000}

        amount = trader.get_sell_amount()

        settings.EXCHANGES['BL3P']['min_sell_value'] = {'BTCEUR': 50000, 'LTCEUR': 5000000}

        assert amount == 0

    @pytest.mark.django_db
    def test_get_buy_amount(self):
        session = mommy.make(Session)
        trader = Trader(session_id=session.id)

        amount = trader.get_buy_amount(7500)

        assert amount == 1333333333333

    @pytest.mark.django_db
    def test_get_buy_max_value(self):
        session = mommy.make(Session)
        trader = Trader(session_id=session.id)

        settings.EXCHANGES['BL3P']['max_buy_value'] = {'BTCEUR': 100, 'LTCEUR': 100}

        amount = trader.get_buy_amount(100000000)

        settings.EXCHANGES['BL3P']['max_buy_value'] = {'BTCEUR': 100000000, 'LTCEUR': 100000000}

        assert amount == 100

    @pytest.mark.django_db
    def test_get_buy_min_value(self):
        session = mommy.make(Session)
        trader = Trader(session_id=session.id)

        settings.EXCHANGES['BL3P']['min_buy_value'] = {'BTCEUR': 10000000, 'LTCEUR': 10000000}

        amount = trader.get_buy_amount(100000000)

        settings.EXCHANGES['BL3P']['max_buy_value'] = {'BTCEUR': 10000000, 'LTCEUR': 5000000}

        assert amount == 100000000
