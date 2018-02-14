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
                'trades': '{pair}/trades',
                'ticker': '{pair}/ticker',
            }
        },
        'private': {
            'url': 'https://api.bl3p.eu/1/',
            'public_key': '!CHANGE-ME!',
            'private_key': '!CHANGE-ME!',
            'paths': {
                'get_balance': 'GENMKT/money/info',
                'add_order': '{pair}/money/order/add',
                'get_order': '{pair}/money/order/result'
            }
        },
        'pairs': {
            'BTC': 'BTCEUR',
            'LTC': 'LTCEUR'
        },
        'min_buy_value': {
            'BTCEUR': 10000000,         # 100 EUR (*1e5)
            'LTCEUR': 5000000,          # 50 EUR
        },
        'min_sell_value': {
            'BTCEUR': 50000,            # 0.0005 BTC (*1e8)
            'LTCEUR': 5000000,          # 0.05 LTC (*1e8)
        },
        'max_buy_value': {
            'BTCEUR': 250000000,        # 2500 EUR
            'LTCEUR': 100000000,        # 1000 EUR
        },
        'max_sell_value': {
            # 'BTCEUR': 100000000,      # 1 BTC
            'BTCEUR': -1,               # Unlimited
            'LTCEUR': -1,               # Unlimited
        },
        'trade_fee': 0.255,             # TODO: replace by value from API
        'soft_run': True,               # dont send orders to exchage
        'intercalate_trade': True,      # intercalte buy and sell orders
        'safe_buy': True,               # dont buy high
        'safe_sell': True,              # dont sell cheap
    }
}
