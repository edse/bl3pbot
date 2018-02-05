from django.core.management.base import BaseCommand
from django.conf import settings
import json
import websocket

from trader.analyser import Analyser
from trader.storage import Storage
from trader.trader import Trader
from trader.models import Session
from trader.base import *  # noqa

# def parse(message):
#     data = json.loads(message)
#     price = float(data['price_int']) / NORM_PRICE
#     amount = float(data['amount_int']) / NORM_AMOUNT
#     return Storage.store([{
#         'measurement': 'BTC_EUR',
#         'tags': {
#             'asset': 'BTC',
#             'currency': 'EUR'
#         },
#         'fields': {
#             'timestamp': data['date'],
#             'price': price,
#             'amount': amount
#         }
#     }])


# def on_message(ws, message, session=session):
#     data = parse(message)[0]
#     result = Analyser.analyse(session, data)

#     trader.take_action(
#         trend=result.trend,
#         current=result.current
#     )


# def on_error(ws, error):
#     logger.log('error', error)


# def run():
#     session = Session.objects.create(
#         status=Session.RUNNING,
#         ma1=settings.BOT_DATA_SAMPLE_MA1,
#         ma2=settings.BOT_DATA_SAMPLE_MA2,
#         data_range=settings.BOT_DATA_SAMPLE_RANGE,
#         data_group=settings.BOT_DATA_SAMPLE_GROUP,
#         data_interval=settings.BOT_TICKER_INTERVAL
#     )
#     trader = Trader(session_id=session.id) # noqa
#     session.start()

#     logger.log('session', 'Session #{} created'.format(session.id))
#     logger.log('start', 'Bot running')

#     ws = websocket.WebSocketApp(
#         get_trades_path(),
#         on_message=on_message,
#         on_error=on_error
#     )
#     ws.run_forever()


# def get_trades_path():
#     return settings.EXCHANGES['BL3P']['public']['wss'] + \
#         settings.EXCHANGES['BL3P']['public']['paths']['trades']


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         run()


class Bl3pWebSocket(websocket.WebSocketApp):
    session = None
    trader = None


class Command(BaseCommand):
    def handle(self, *args, **options):
        echo_settings()
        run()


def get_trades_path():
    return settings.EXCHANGES['BL3P']['public']['wss'] + \
        settings.EXCHANGES['BL3P']['public']['paths']['trades']


def parse(message):
    data = json.loads(message)
    price = float(data['price_int']) / NORM_PRICE
    amount = float(data['amount_int']) / NORM_AMOUNT
    return Storage.store([{
        'measurement': 'BTC_EUR',
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
    data = parse(message)[0]
    result = Analyser.analyse(ws.session, data)

    ws.trader.take_action(
        trend=result.trend,
        current=result.current
    )


def on_error(ws, error):
    logger.log('error', error)
    logger.log('restarting...', '')
    run()


def on_close(ws):
    logger.log('closed', '"### closed ###"')


def run():
    websocket.enableTrace(True)
    session = Session.objects.create(
        status=Session.RUNNING,
        ma1=settings.BOT_DATA_SAMPLE_MA1,
        ma2=settings.BOT_DATA_SAMPLE_MA2,
        ma3=settings.BOT_DATA_SAMPLE_MA3,
        data_range=settings.BOT_DATA_SAMPLE_RANGE,
        data_group=settings.BOT_DATA_SAMPLE_GROUP,
        data_interval=settings.BOT_TICKER_INTERVAL
    )
    trader = Trader(session_id=session.id) # noqa
    session.start()

    logger.log('session', 'Session #{} created'.format(session.id))
    logger.log('start', 'Bot running')

    ws = Bl3pWebSocket(
        get_trades_path(),
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
    logger.log('safe_trade', settings.EXCHANGES['BL3P']['safe_trade'])
