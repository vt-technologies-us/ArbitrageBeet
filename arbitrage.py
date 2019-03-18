import asyncio
import difflib
import threading

import numpy as np
import tabulate

import basics
import exchanges

_condition = threading.Condition()
_api_num = len(exchanges.all_apis)
_exchanges_flags = [False] * _api_num


class PairAnalysisThread(threading.Thread):
    def __init__(self, sender):
        super(self.__class__, self).__init__()
        self.pair_flags = np.eye(_api_num)  # [[False] * _api_num for _ in range(_api_num)]
        self.sender = sender
        self.should_kill = False

    # @staticmethod
    def find_arbitrage(self, ex_i, ex_j, amount=1):
        if ex_i.ask_bid_list is None or ex_j.ask_bid_list is None:
            return

        joints_key = []
        joints_value = []
        for k_i in ex_i.ask_bid_list:
            k_matched = difflib.get_close_matches(k_i, ex_j.ask_bid_list.keys(), cutoff=0.9)
            if k_matched:
                k_j = k_matched[0]
                joints_key.append([k_i, k_j])
                joints_value.append([ex_i.ask_bid_list[k_i][0], ex_i.ask_bid_list[k_i][1],
                                     ex_j.ask_bid_list[k_j][0], ex_j.ask_bid_list[k_j][1], ])

        if len(joints_key) <= 0:
            return

        pairs_key = np.array(joints_key)
        pairs_ask_bid = np.array(joints_value)
        pairs_ask_bid, pairs_key = pairs_ask_bid[~np.any(pairs_ask_bid == '--', axis=1)].astype(np.float64), \
                                   pairs_key[~np.any(pairs_ask_bid == '--', axis=1)]

        arb = (amount / pairs_ask_bid[:, 1] * (1 - ex_i.fee)) * pairs_ask_bid[:, 2] * (1 - ex_j.fee) / amount
        keys, arb = pairs_key[arb > 1], arb[arb > 1]
        keys, arb = keys[arb < 2], arb[arb < 2]

        if arb.shape[0] <= 0:
            return

        ind = arb.argsort()[::-1]
        result = np.concatenate((keys[ind], arb[ind].reshape((-1, 1))), axis=1)
        self.sender(tabulate.tabulate(result, headers=[ex_i.exchange_name, ex_j.exchange_name, 'percent']))

        return result

    def run(self):
        while not self.should_kill and not all(all(pair_row) for pair_row in self.pair_flags):
            _condition.acquire()
            _condition.wait()

            for i in range(_api_num):
                for j in set(range(_api_num)).difference({i}):
                    if _exchanges_flags[i] and _exchanges_flags[j] and not self.pair_flags[i][j]:
                        self.pair_flags[i][j] = True
                        self.find_arbitrage(exchanges.all_apis[i], exchanges.all_apis[j])

            _condition.release()


async def get_ticker(i, ex: basics.AbstractAPI):
    result = await ex.get_ticker()
    _condition.acquire()
    _condition.notify()
    _exchanges_flags[i] = True
    _condition.release()
    return result


async def get_raw_data():
    tickers = zip(exchanges.all_apis,
                  await asyncio.gather(*[get_ticker(i, ex) for i, ex in enumerate(exchanges.all_apis)]))
    return tickers


def find_arbitrage(sender):
    pair_analyser = PairAnalysisThread(sender)
    pair_analyser.start()
    asyncio.run(get_raw_data())
    pair_analyser.join(timeout=5)
    if pair_analyser.is_alive():
        pair_analyser.should_kill = True
    sender('request completed')


if __name__ == '__main__':
    find_arbitrage(print)
