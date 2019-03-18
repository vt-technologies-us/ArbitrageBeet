import asyncio

import basics


class BinanceAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://api.binance.com/api/v1/ticker/24hr'
    _book = 'https://api.binance.com/api/v1/depth?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for record in data:
            res[record.get('symbol')] = record.get('bidPrice', None), record.get('askPrice', None)

        return res


class KucoinAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://api.kucoin.com/v1/open/tick'
    _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        if not data.get('success', False):
            return None
        for record in data['data']:
            res[record.get('symbol')] = record.get('buy', None), record.get('sell', None)

        return res


class CobinHoodAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://api.cobinhood.com/v1/market/tickers'
    _book = 'https://api.cobinhood.com//v1/market/orderbooks/:{}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for record in data['result']['tickers']:
            res[record.get('trading_pair_id')] = record.get( 'highest_bid', None), record.get('lowest_ask', None)

        return res


class CoinexAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://api.coinex.com/v1/market/ticker/all'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for symbol, record in data['data']['ticker'].items():
            res[symbol] = record.get('buy', None), record.get('sell', None)

        return res


class LBankAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://api.lbkex.com/v1/ticker.do?symbol=all'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for record in data:
            res[record.get('symbol', None).upper()] = \
                record.get('ticker', None).get('high', None), \
                record.get('ticker', None).get('low', None)

        return res


class ZBAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'http://api.zb.cn/data/v1/allTicker'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for symbol, record in data.items():
            res[symbol.upper()] = record.get('buy', None), record.get('sell', None)

        return res


class GateIOAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://data.gateio.co/api2/1/tickers'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for symbol, record in data.items():
            res[symbol.upper()] = record.get('highestBid', None), record.get('lowestAsk', None)

        return res


class HitBTCAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://api.hitbtc.com/api/2/public/ticker'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for record in data:
            res[record.get('symbol', None)] = record.get('bid', None), record.get('ask', None)

        return res


class OkexAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://www.okex.com/api/spot/v3/instruments/ticker'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for record in data:
            res[record.get('instrument_id', None)] = record.get(
                'best_bid', None), record.get('best_ask', None)

        return res


class CoinbaseAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'http://api.coinbene.com/v1/market/ticker?symbol=all'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for record in data['ticker']:
            res[record.get('symbol', None)] = record.get(
                'bid', None), record.get('ask', None)

        return res


class DigifinexAPI(basics.AbstractAPI, metaclass=basics.Singleton):
    ticker = 'https://openapi.digifinex.com/v2/ticker?apiKey=15c684d41d6eba'

    # _book = 'https://api.kucoin.com/v1/open/orders?symbol={}&limit=20'

    def _format_ticker(self, data):
        res = {}
        for symbol, record in data['ticker'].items():
            res[symbol] = record.get('buy', None), record.get('sell', None)

        return res


all_apis = [api() for api in basics.inheritors(basics.AbstractAPI)]


async def get_raw_data():
    tickers = zip([ex.exchange_name for ex in all_apis],
                  await asyncio.gather(*[ex.get_ticker() for ex in all_apis]))
    return dict(tickers)


if __name__ == '__main__':
    print(asyncio.run(get_raw_data()))

    # b = DigifinexAPI()
    # res = asyncio.run(b.get_ticker())
    # print(res)
