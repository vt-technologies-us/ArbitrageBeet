import asyncio
import datetime
import json
import os

import aiohttp

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open('secrets.json') as f:
    secrets = json.load(f)


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


async def get_url(url):
    """Nothing to see here, carry on ..."""

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            return await response.text(), response.status


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AbstractAPI:
    fee = 0.001
    ticker = ''
    _book = ''
    symbols = {}

    def __init__(self):
        self.ask_bid_list = None

    @property
    def exchange_name(self):
        return self.__class__.__name__[:-3].lower()

    @property
    def api_key(self):
        return secrets[self.exchange_name]['api_key']

    @property
    def secret(self):
        return secrets[self.exchange_name]['secret']

    def book(self, symbol):
        return self._book.format(symbol)

    async def get_ticker(self):
        try:
            raw, status = await get_url(self.ticker)
            data = json.loads(raw)
        except asyncio.TimeoutError as _:
            data = {
                'time': datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S'),
                'error': 'timeout',
                # 'err': err.with_traceback()
            }
            # print(data)
        except aiohttp.client_exceptions.ClientConnectorError as err:
            data = {
                'time': datetime.datetime.now().strftime('%y/%m/%d %H:%M:%S'),
                'error': err.strerror,

                # 'err': err.with_traceback()
            }

        if 'error' in data:
            print(f'{self.exchange_name}: {data}')
            return data

        self.ask_bid_list = self._format_ticker(data)
        return self.ask_bid_list

    def _format_ticker(self, data):
        pass
