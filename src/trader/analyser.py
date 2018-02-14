from collections import namedtuple

from .base import *  # noqa
from .storage import Storage

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
        pair = session.pair
        diff_measurement = '{pair}_MA1_MA2_DIFF'.format(pair=pair)

        macd = []
        signal = []

        # SIGNAL
        q = """SELECT moving_average(mean("diff"), {ma3}) as ma3,
            mean("diff") as diff
            FROM "{diff_measurement}"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            diff_measurement=diff_measurement,
            pair=pair,
            ma3=ma3,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement=diff_measurement))) > 1:
            try:
                signal.append(list(rs.get_points(measurement=diff_measurement))[-2]['ma3'])
                signal.append(list(rs.get_points(measurement=diff_measurement))[-1]['ma3'])

                _signal = float(list(rs.get_points(measurement=diff_measurement))[-1]['ma3'])
                _macd = float(list(rs.get_points(measurement=diff_measurement))[-1]['diff'])
                _hist = _macd - _signal

                Storage.store([{
                    'measurement': '{pair}_MACD'.format(pair=pair),
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
            except Exception as e:
                logger.log('error', e)
                pass

        # MACD
        q = """SELECT mean("diff") as diff
            FROM "{diff_measurement}"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(previous)""".format(
            diff_measurement=diff_measurement,
            pair=pair,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        if len(list(rs.get_points(measurement=diff_measurement))) > 1:
            macd.append(list(rs.get_points(measurement=diff_measurement))[-2]['diff'])
            macd.append(list(rs.get_points(measurement=diff_measurement))[-1]['diff'])

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
                'measurement': '{pair}_TREND'.format(pair=pair),
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
    def analyse(session):
        range = session.data_range
        group = session.data_group
        ma1 = session.ma1
        ma2 = session.ma2
        pair = session.pair
        diff_measurement = '{pair}_MA1_MA2_DIFF'.format(pair=pair)

        influx_client = Storage.get_client()
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
            FROM "{pair}"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(previous)""".format(
            pair=pair,
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
            FROM "{pair}"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            pair=pair,
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
            FROM "{pair}"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            pair=pair,
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
            diff = current['ma1'] - current['ma2']

            Storage.store([{
                'measurement': diff_measurement,
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
        return TrendResult(trend, current)
