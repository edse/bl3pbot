import json
import time

import websocket
from django.conf import settings
from django.core.management.base import BaseCommand
from trader.analyser import Analyser
from trader.base import *  # noqa
from trader.models import Session
from trader.storage import Storage
from trader.trader import Trader


class Bl3pWebSocket(websocket.WebSocketApp):
    session = None
    trader = None
    last_analizer_time = 0


class Command(BaseCommand):
    def handle(self, *args, **options):
        echo_settings()
        run()


def get_trades_path(pair):
    return settings.EXCHANGES['BL3P']['public']['wss'] + \
        settings.EXCHANGES['BL3P']['public']['paths']['trades'].format(pair=pair)


def store_data(message, pair):
    data = json.loads(message)
    price = float(data['price_int']) / NORM_PRICE
    amount = float(data['amount_int']) / NORM_AMOUNT
    return Storage.store([{
        'measurement': pair,
        'tags': {
            'asset': 'BTC',
            'currency': 'EUR'
        },
        'fields': {
            'timestamp': data['date'],
            'price': price,
            'amount': amount
        }
    }])


def on_message(ws, message):
    store_data(message, pair=ws.session.pair)
    analize()


def on_error(ws, error):
    logger.log('error', error)
    logger.log('restarting...', '')
    run()


def on_close(ws):
    logger.log('closed', '"### closed ###"')


def analize():
    if time.time() - ws.last_analizer_time >= settings.BOT_ANALIZER_INTERVAL:
        ws.last_analizer_time = time.time()
        logger.log('analysing', 'Session: #{}'.format(ws.session.id))

        result = Analyser.analyse(ws.session)

        ws.trader.take_action(
            trend=result.trend,
            current=result.current
        )


def run():
    websocket.enableTrace(True)
    session = Session.objects.create(
        status=Session.RUNNING,
        ma1=settings.BOT_DATA_SAMPLE_MA1,
        ma2=settings.BOT_DATA_SAMPLE_MA2,
        ma3=settings.BOT_DATA_SAMPLE_MA3,
        data_range=settings.BOT_DATA_SAMPLE_RANGE,
        data_group=settings.BOT_DATA_SAMPLE_GROUP,
        data_interval=settings.BOT_TICKER_INTERVAL,
        pair=settings.BOT_DEFAULT_PAIR,
    )
    trader = Trader(session_id=session.id)
    session.start()

    logger.log('session', 'Session #{} created'.format(session.id))
    logger.log('start', 'Bot running')

    ws = Bl3pWebSocket(
        get_trades_path(session.pair),
        on_message=on_message,
        on_error=on_error
    )
    ws.session = session
    ws.trader = trader
    ws.run_forever()


def echo_settings():
    logger.log('settings', '...')
    logger.log('trade_fee', settings.EXCHANGES['BL3P']['trade_fee'])
    logger.log('min_buy_value', settings.EXCHANGES['BL3P']['min_buy_value'])
    logger.log('min_sell_value', settings.EXCHANGES['BL3P']['min_sell_value'])
    logger.log('max_buy_value', settings.EXCHANGES['BL3P']['max_buy_value'])
    logger.log('max_sell_value', settings.EXCHANGES['BL3P']['max_sell_value'])
    logger.log('soft_run', settings.EXCHANGES['BL3P']['soft_run'])
    logger.log('intercalate_trade', settings.EXCHANGES['BL3P']['intercalate_trade'])
    logger.log('safe_buy', settings.EXCHANGES['BL3P']['safe_buy'])
    logger.log('safe_sell', settings.EXCHANGES['BL3P']['safe_sell'])
