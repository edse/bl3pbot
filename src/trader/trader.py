from trader.analyser import Analyser
from trader.base import *  # noqa
from trader.client import Bl3p
from django.conf import settings
from trader.models import Session, Trade
from trader.storage import Storage


class Trader(object):

    def __init__(self, session_id):
        self.client = Bl3p()
        self.analyser = Analyser()
        if session_id:
            self.session = Session.objects.get(pk=session_id)

    def analyse(self, trend_result):
        self.take_action(
            trend=trend_result['trend'],
            current=trend_result['current']
        )

    def get_sell_amount(self):
        available = 0
        balance = self.client.get_balance()

        if not balance:
            return 0

        if self.session.pair == 'BTCEUR':
            available = int(balance['data']['wallets']['BTC']['available']['value_int'])
        elif self.session.pair == 'LTCEUR':
            available = int(balance['data']['wallets']['LTC']['available']['value_int'])
        else:
            return 0

        if available < settings.EXCHANGES['BL3P']['min_sell_value'][self.session.pair]:
            logger.log('amount', 'Amount available ({}) is smaller than min_sell_value ({})'.format(
                available, settings.EXCHANGES['BL3P']['min_sell_value'][self.session.pair]
            ))
            return 0

        if settings.EXCHANGES['BL3P']['max_sell_value'][self.session.pair] > 0:
            if available > settings.EXCHANGES['BL3P']['max_sell_value'][self.session.pair]:
                available = settings.EXCHANGES['BL3P']['max_sell_value'][self.session.pair]

        return available

    def get_buy_amount(self, price):
        available = 0
        balance = self.client.get_balance()

        if balance:
            available = int(balance['data']['wallets']['EUR']['available']['value_int'])

        if settings.EXCHANGES['BL3P']['min_buy_value'][self.session.pair] > 0:
            if available < settings.EXCHANGES['BL3P']['min_buy_value'][self.session.pair]:
                logger.log('amount', 'EUR amount available ({}) is smaller than min_buy_value  ({})'.format(
                    available, settings.EXCHANGES['BL3P']['min_buy_value'][self.session.pair]
                ))
                return 0

        if settings.EXCHANGES['BL3P']['max_buy_value'][self.session.pair] > 0:
            if available > settings.EXCHANGES['BL3P']['max_buy_value'][self.session.pair]:
                available = settings.EXCHANGES['BL3P']['max_buy_value'][self.session.pair]

        return int(available / price * NORM_AMOUNT)

    def store_trade(self, params, order_id=0):
        logger.log('trade', str(params))

        amount = float(params['amount_int']) / NORM_AMOUNT
        price = float(params['price_int']) / NORM_PRICE
        fee = float(settings.EXCHANGES['BL3P']['trade_fee'])
        total = (price * amount) + (((price * amount) / 100) * fee)

        # Influx
        stored = Storage.store([{
            'measurement': '{pair}_TRADE'.format(pair=self.session.pair),
            'tags': {
                'asset': params['type'],
            },
            'fields': {
                'price': price,
                'amount': amount,
                'total': total,
                'trend': 10 if params['type'] == 'bid' else -10
            }
        }])

        # Django
        Trade.objects.create(
            session_id=self.session.id,
            order_id=int(order_id),
            amount=amount,
            price=price,
            total=total,
            fee=fee,
            type=Trade.BUY if params['type'] == 'bid' else Trade.SELL
        )

        logger.log('store', str(stored))

    def buy(self, price):
        price = int(price * NORM_PRICE)
        amount = self.get_buy_amount(price)
        params = {
            'type': 'bid',
            'amount_int': amount,
            'price_int': price,
            'fee_currency': 'BTC' if self.session.pair == 'BTCEUR' else 'LTCEUR'
        }

        """
        " SAFE BUY
        """
        if settings.EXCHANGES['BL3P']['safe_buy']:
            # check if the buy price + fees is cheaper than the last sell
            last_order = Trade.objects.filter(type=Trade.SELL).last()

            if not last_order:
                return False

            _amount = float(params['amount_int']) / NORM_AMOUNT
            _price = float(params['price_int']) / NORM_PRICE
            _fee = float(settings.EXCHANGES['BL3P']['trade_fee'])
            _total = (_price * _amount) + (((_price * _amount) / 100) * _fee)

            if _total > last_order.total:
                logger.log(
                    'safe_buy',
                    'Trying to buy for a higher price than the last sell with safe_trade set to true!'
                )
                logger.log(
                    'safe_buy',
                    'Current price: {} Last trade price + fees: {}'.format(price, last_order.price)
                )
                return False

        if amount <= 0:
            return False

        response = self.client.add_order(params, self.session.pair)

        if response:
            self.store_trade(params, response['data']['order_id'])
        else:
            self.store_trade(params)

    def sell(self, price):
        price = int(price * NORM_PRICE)
        amount = self.get_sell_amount()
        params = {
            'type': 'ask',
            'amount_int': amount,
            'price_int': price,
            'fee_currency': 'BTC' if self.session.pair == 'BTCEUR' else 'LTCEUR'
        }

        """
        " SAFE SELL
        """
        if settings.EXCHANGES['BL3P']['safe_sell']:
            # check if the sell price is higher than the last buy + fees
            last_order = Trade.objects.filter(type=Trade.BUY).last()

            if not last_order:
                return False

            _price = float(params['price_int']) / NORM_PRICE
            _fee = float(settings.EXCHANGES['BL3P']['trade_fee'])
            _total = _price + ((_price / 100) * _fee)

            if _total <= last_order.total:
                logger.log(
                    'safe_sell',
                    'Trying to sell for a cheaper price than the last buy with safe_trade set to true!'
                )
                logger.log(
                    'safe_sell',
                    'Current price: {} Last trade price + fees: {}'.format(price, last_order.total)
                )
                return False

        if amount <= 0:
            return False

        response = self.client.add_order(params, self.session.pair)

        if response:
            self.store_trade(params, response['data']['order_id'])
        else:
            self.store_trade(params)

    def get_order(self, order_id):
        params = {'order_id': order_id}
        return self.client.get_order(params)

    def take_action(self, trend, current):
        price = float(current['price'])
        last_order = Trade.objects.all().last()

        if trend == 1:
            logger.log('up', price)
        elif trend == -1:
            logger.log('down', price)

        if trend == 10:
            logger.log('buy', price)
            if last_order:
                if settings.EXCHANGES['BL3P']['intercalate_trade']:
                    # last order must be a sell
                    if last_order.type == Trade.BUY:
                        logger.log(
                            'intercalate_trade',
                            'Trying to buy after a buy with intercalate_trade set to true!'
                        )
                        return False
            # BUY
            self.buy(price)

        elif trend == -10:
            logger.log('sell', price)
            if last_order:
                if settings.EXCHANGES['BL3P']['intercalate_trade']:
                    # last order must be a buy
                    if last_order.type == Trade.SELL:
                        logger.log(
                            'intercalate_trade',
                            'Trying to sell after a sell with intercalate_trade set to true!'
                        )
                        return False
            # SELL
            self.sell(price)
