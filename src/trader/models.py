from django.db import models
from django.utils import timezone


class Advice(models.Model):
    pair = models.CharField(max_length=30)
    position = models.CharField(max_length=30)
    diff = models.FloatField(default=0)
    price = models.FloatField()
    tweet = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Session(models.Model):
    RUNNING = 'RUNNING'
    ENDED = 'ENDED'
    SESSION_STATUSES = (
        (RUNNING, 'Running'),
        (ENDED, 'Ended'),
    )

    status = models.CharField(choices=SESSION_STATUSES, max_length=25)
    ma1 = models.PositiveSmallIntegerField(default=12)
    ma2 = models.PositiveSmallIntegerField(default=26)
    ma3 = models.PositiveSmallIntegerField(default=9)
    data_range = models.CharField(default='3h', max_length=25)
    data_group = models.CharField(default='1m', max_length=25)
    data_interval = models.CharField(default='10', max_length=25)
    btc_balance_at_start = models.FloatField(default=0)
    euro_balance_at_start = models.FloatField(default=0)
    btc_balance = models.FloatField(default=0)
    euro_balance = models.FloatField(default=0)
    pair = models.CharField(default='BTCEUR', max_length=16)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def start(self):
        self.status = self.RUNNING
        self.started_at = timezone.now()
        self.save()

    def __str__(self):
        return '#{} - {}'.format(
            self.id, self.status
        )


class Trade(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRADE_TYPES = (
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    )

    session = models.ForeignKey(Session, related_name='trades', default=0, on_delete=models.CASCADE)
    order_id = models.IntegerField(default=0)
    amount = models.FloatField()
    price = models.FloatField()
    total = models.FloatField()
    fee = models.FloatField()
    type = models.CharField(choices=TRADE_TYPES, max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '#{} - {}: {} ({})'.format(
            self.id, self.type, self.amount, self.price
        )
