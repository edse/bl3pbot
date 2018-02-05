from emoji import emojize
from datetime import datetime
from colorama import Fore, Back, Style, init


class Logger(object):
    first_name = 'Bl3p'
    last_name = 'Bot'
    title_len = 24
    backgrounds = {
        'start': Back.WHITE,
        'buy': Back.MAGENTA,
        'sell': Back.MAGENTA,
        'up': Back.GREEN,
        'down': Back.RED,
        'soft_run': Back.BLUE,
        'intercalate_trade': Back.BLUE,
        'safe_trade': Back.BLUE,
    }
    foregrounds = {
        'start': Fore.BLACK,
    }
    emojis = {
        'start': ':checkered_flag: ',
        'buy': ':gift_heart: ',
        'sell': ':sparkling_heart: ',
        'up': ':chart_with_upwards_trend: ',
        'down': ':chart_with_downwards_trend: ',
        'soft_run': ':raised_hand: :cop: ',
        'intercalate_trade': ':raised_hand: :cop: ',
        'safe_trade': ':raised_hand: :cop: ',
    }

    def __init__(self):
        init(autoreset=True)

    def get_name(self):
        return (Style.BRIGHT + Back.BLUE + '[ ' + self.first_name +
                Back.MAGENTA + self.last_name + ' ]' + Style.RESET_ALL + ' ')

    def get_time(self):
        return ' ' + Style.DIM + str(datetime.now()) + Style.RESET_ALL + ' '

    def get_background(self, key):
        return self.backgrounds[key] if key in self.backgrounds else ''

    def get_foreground(self, key):
        return self.foregrounds[key] if key in self.foregrounds else ''

    def get_emoji(self, key):
        return emojize(self.emojis[key], use_aliases=True) if key in self.emojis else ''

    def get_title(self, title, background=None, foreground=None):
        # import ipdb; ipdb.set_trace()
        size = len(title)
        rest = self.title_len - size
        padding = ' ' * int(round(rest / 2))
        _title = padding + title + padding

        if len(_title) > self.title_len:
            _title = _title[:self.title_len - (len(_title) - self.title_len)]

        if len(_title) < self.title_len:
            _title = _title + ' ' * (self.title_len - len(_title))

        bg = background if background else self.get_background(title)
        fg = foreground if foreground else self.get_foreground(title)
        return ' ' + Style.BRIGHT + bg + fg + ' ' + _title + ' ' + Style.RESET_ALL + ' '

    def get_values(self, value, title):
        return self.get_emoji(title) + ' ' + str(value) + ' ' + Style.RESET_ALL

    def get_line(self, title, values):
        return ' ' + self.get_name() + self.get_time() + \
            self.get_title(title) + self.get_values(values, title)

    def log(self, title, values):
        print(self.get_line(title, values))
