from django.conf import settings
from tests.base import BaseTestCase
from trader.analyser import Analyser
from trader.models import Session
# from model_mommy import mommy


class TestAnalyser(BaseTestCase):

    def test_soft_run(self):
        pass
        # session = mommy.make(
        #     Session,
        #     ma1=settings.BOT_DATA_SAMPLE_MA1,
        #     ma2=settings.BOT_DATA_SAMPLE_MA2,
        #     ma3=settings.BOT_DATA_SAMPLE_MA3,
        #     data_range=settings.BOT_DATA_SAMPLE_RANGE,
        #     data_group=settings.BOT_DATA_SAMPLE_GROUP,
        #     data_interval=settings.BOT_TICKER_INTERVAL
        # )

        # current = {
        #     'time': 1,
        #     'price': 100,
        #     'ma1': 12,
        #     'ma2': 26,
        # }

        # Analyser.checkTrend(session, current)
