# TWITTER
TWITTER_CONSUMER_KEY = '!CHANGE-ME!'
TWITTER_CONSUMER_SECRET = '!CHANGE-ME!'
TWITTER_ACCESS_TOKEN = '!CHANGE-ME!'
TWITTER_ACCESS_TOKEN_SECRET = '!CHANGE-ME!'

# DJANGO
SECRET_KEY = '!CHANGE-ME!'
DEBUG = True

# EXCHANGES
EXCHANGES = {
    'BL3P': {
        'name': 'BL3P',
        'public': {
            'http': 'https://api.bl3p.eu/1/',
            'wss': 'wss://api.bl3p.eu/1/',
            'paths': {
                'trades': 'BTCEUR/trades',
                'ticker': 'BTCEUR/ticker',
            }
        },
        'private': {
            'url': 'https://api.bl3p.eu/1/',
            'public_key': '!CHANGE-ME!',
            'private_key': '!CHANGE-ME!',
            'paths': {
                'get_balance': 'GENMKT/money/info',
                'add_order': 'BTCEUR/money/order/add',
                'get_order': 'BTCEUR/money/order/result'
            }
        },
        'trade_fee': 0.255,           # TODO: replace by value from API
        'min_buy_value': 1000000,     # TODO: 10 EUR (*1e5)
        'min_sell_value': 50000,      # TODO: 0.0005 BTC (*1e8)
        'max_buy_value': 100000000,   # TODO: 1000 EUR
        'max_sell_value': 100000000,  # TODO: 1 BTC
        'soft_run': True,             # dont send orders to exchage
        'intercalate_trade': True,    # intercalte buy and sell orders
        'safe_buy': True,             # dont buy high
        'safe_sell': True,            # dont sell cheap
    }
}
