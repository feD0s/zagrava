import sys

import ccxt
import pandas as pd
from ccxt.base.decimal_to_precision import ROUND_UP

MSEC = 1000
MINUTE = 60 * MSEC


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


def get_candlesDf(exchange, cfg: dict, windowSize: int, interval: float) -> pd.DataFrame:
    # used some code from: https://github.com/ccxt/ccxt/blob/master/examples/py/fetch-ohlcv-on-new-candle.py
    timeframe = cfg['timeframe']
    # get candles for timelimit + windowSize period to calculate ema correctly for timelimit period
    timeLimit = cfg['timeLimit'] + windowSize
    symbol = cfg['symbol']
    try:
        since = exchange.round_timeframe(
            timeframe, exchange.milliseconds(), ROUND_UP) - (timeLimit * interval)
        ohlcv = exchange.fetch_ohlcv(symbol.replace(
            "/", ""), timeframe, since=since, limit=timeLimit)
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error', type(error).__name__, error.args)
    # leave only updatetime and close price columns
    candlesDf = pd.DataFrame(
        ohlcv, columns=['updatetime', 'open', 'high', 'low', 'close', 'volume'])
    candlesDf = candlesDf[['updatetime', 'close']]
    # calculate simple moving average
    candlesDf['ma'] = candlesDf['close'].rolling(windowSize).mean()
    # cut first windowSize rows because their MA is not calculated correctly
    candlesDf = candlesDf[windowSize:].reset_index(drop=True)
    return candlesDf
