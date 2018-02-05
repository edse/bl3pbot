from collections import namedtuple
# from django.conf import settings
from .storage import Storage
from .base import *  # noqa


TrendResult = namedtuple('Trend', ['trend', 'current'])


class Analyser(object):
    @staticmethod
    def checkTrend(session, current):
        """
        Check the last 2 records from the last 30m grouped by 1m
        Returns:
            int(-10): when the trending is down and a sell action is required
            int(-1): when the trending is down
            int(0): when in no trend or no enough data
            int(1): when the trending is up
            int(10): when the trending is up and a sell action is required
        """
        trend = 0
        state = 'No trend'
        influx_client = Storage.get_client()

        range = session.data_range
        group = session.data_group
        ma3 = session.ma3

        macd = []
        signal = []

        # SIGNAL
        q = """SELECT moving_average(mean("diff"), {ma3}) as ma3,
            mean("diff") as diff
            FROM "MA1_MA2_DIFF"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            ma3=ma3,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement='MA1_MA2_DIFF'))) > 1:
            signal.append(list(rs.get_points(measurement='MA1_MA2_DIFF'))[-2]['ma3'])
            signal.append(list(rs.get_points(measurement='MA1_MA2_DIFF'))[-1]['ma3'])

            _signal = float(list(rs.get_points(measurement='MA1_MA2_DIFF'))[-1]['ma3'])
            _macd = float(list(rs.get_points(measurement='MA1_MA2_DIFF'))[-1]['diff'])
            _hist = _macd - _signal

            Storage.store([{
                'measurement': 'MACD',
                'tags': {
                    'asset': 'MA3',
                    'currency': 'MACD'
                },
                'fields': {
                    'timestamp': current['time'],
                    'signal': _signal,
                    'macd': _macd,
                    'hist': _hist,
                }
            }])

        # MACD
        q = """SELECT mean("diff") as diff
            FROM "MA1_MA2_DIFF"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(previous)""".format(
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement='MA1_MA2_DIFF'))) > 1:
            macd.append(list(rs.get_points(measurement='MA1_MA2_DIFF'))[-2]['diff'])
            macd.append(list(rs.get_points(measurement='MA1_MA2_DIFF'))[-1]['diff'])

        if macd and signal:
            h0 = macd[0] - signal[0]
            h1 = macd[1] - signal[1]

            if h0 < h1:
                # up trend
                if h0 <= 0 and h1 >= 0:
                    trend = 10  # buy action
                    state = 'buy'
                else:
                    trend = 1
                    state = 'up'

            if h0 > h1:
                # down trend
                if h1 <= 0 and h0 >= 0:
                    trend = -10  # sell action
                    state = 'sell'
                else:
                    trend = -1
                    state = 'down'

            if h0 == h1:
                # no trend
                trend = 0
                state = 'horizontal'

            Storage.store([{
                'measurement': 'TREND',
                'tags': {
                    'state': state,
                },
                'fields': {
                    'trend': trend
                }
            }])

            return trend

        else:
            return 0

    @staticmethod
    def analyse(session, data):
        # range = settings.BOT_DATA_SAMPLE_RANGE  # 3h
        # group = settings.BOT_DATA_SAMPLE_GROUP  # 1m
        # ma1 = settings.BOT_DATA_SAMPLE_MA1      # 10
        # ma2 = settings.BOT_DATA_SAMPLE_MA2      # 20

        range = session.data_range
        group = session.data_group
        ma1 = session.ma1
        ma2 = session.ma2

        influx_client = Storage.get_client()
        pair = data['measurement']
        # tweet = None
        # position = ''
        current = {
            'time': None,
            'price': None,
            'ma1': None,
            'ma2': None,
        }

        #
        # TODO: Replace 3 queries by 1
        #
        q = """SELECT mean("price") as price
            FROM "BTC_EUR"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(previous)""".format(
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement=pair))) > 0:
            r = list(rs.get_points(measurement=pair))[-1]
            if 'price' in r:
                current['price'] = r['price']
                current['time'] = r['time']

        q = """SELECT moving_average(mean("price"), {ma1}) as ma1
            FROM "BTC_EUR"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            ma1=ma1,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement=pair))) > 1:
            r = list(rs.get_points(measurement=pair))[-1]
            if 'ma1' in r:
                current['ma1'] = r['ma1']

        q = """SELECT moving_average(mean("price"), {ma2}) as ma2
            FROM "BTC_EUR"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            ma2=ma2,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement=pair))) > 1:
            r = list(rs.get_points(measurement=pair))[-1]
            if 'ma2' in r:
                current['ma2'] = r['ma2']

        if current['time'] and current['price'] and current['ma1'] and current['ma2']:
            # diff
            diff = current['ma1'] - current['ma2']

            Storage.store([{
                'measurement': 'MA1_MA2_DIFF',
                'tags': {
                    'asset': 'MA1',
                    'currency': 'MA2'
                },
                'fields': {
                    'timestamp': current['time'],
                    'diff': float(diff),
                    'ma1': float(current['ma1']),
                    'ma2': float(current['ma2']),
                }
            }])

        trend = Analyser.checkTrend(session, current)
        # logger.log('trend', trend)
        return TrendResult(trend, current)
