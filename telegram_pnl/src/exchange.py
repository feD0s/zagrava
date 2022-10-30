import sys

import ccxt
import pandas as pd
from ccxt.base.decimal_to_precision import ROUND_UP

msec = 1000
minute = 60 * msec
hold = 30


def get_exchange_client(exchange, log):
    if exchange == 'binance':
        client = ccxt.binance({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # futures contracts
            },
        })
        return client
    else:
        log.error('Exchange not supported')
        sys.exit()


def get_candlesDf(exchange, cfg: dict, windowSize: int) -> pd.DataFrame:
    # used some code from: https://github.com/ccxt/ccxt/blob/master/examples/py/fetch-ohlcv-on-new-candle.py
    timeframe = cfg['timeframe']
    timeLimit = cfg['timeLimit']
    interval = cfg['interval']
    symbol = cfg['symbol']
    try:
        since = exchange.round_timeframe(
            timeframe, exchange.milliseconds(), ROUND_UP) - (timeLimit * interval)
        ohlcv = exchange.fetch_ohlcv(symbol.replace(
            "/", ""), timeframe, since=since, limit=timeLimit)
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error', type(error).__name__, error.args)
    # leave only updatetime and close price columns and calculate simple moving average
    candlesDf = pd.DataFrame(
        ohlcv, columns=['updatetime', 'open', 'high', 'low', 'close', 'volume'])
    candlesDf = candlesDf[['updatetime', 'close']]
    candlesDf['ma'] = candlesDf['close'].rolling(windowSize).mean()
    # cut first windowSize rows to calculate ewma properly
    candlesDf = candlesDf[windowSize:].reset_index(drop=True)
    return candlesDf