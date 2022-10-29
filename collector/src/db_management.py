import os
import time

import pandas as pd
import psycopg2 as pg

# db parameters
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_IP = os.getenv('DB_IP')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')


def get_db_engine():
    '''get db engine'''
    engine = pg.connect(user=DB_USER,
                        password=DB_PASSWORD,
                        host=DB_IP,
                        port=DB_PORT,
                        database=DB_NAME)
    return engine


def check_candles_table(symbol: str, exchange: str, log):
    '''check if candles table exists in database'''
    candlesTableName = exchange + '_candles_' + symbol.replace("/", "").lower()
    try:
        # Connect to an existing database
        engine = get_db_engine()
        cursor = engine.cursor()
        # check if database exists
        cursor.execute(
            "select exists(select * from information_schema.tables where table_name=%s)", (candlesTableName,))
        result = cursor.fetchone()[0]
        if result == True:
            log.debug('Table candles exists')
        else:
            log.debug("Table candles doesn't exist")
    except (Exception, pg.Error) as error:
        result = False
        log.debug(
            'Error while connecting to PostgreSQL: {error}'.format(error=error))
    finally:
        if engine:
            cursor.close()
            engine.close()
            log.debug("PostgreSQL connection is closed")
        return result


def get_candlesDf(symbol: str, exchange: str, log, hoursAgo=300):
    '''get candles from database for last 300 hours'''
    tableName = exchange + '_candles_' + symbol.replace("/", "").lower()
    # считаем время для отсечки датафреймов в миллисекундах
    n_miliseconds = int(hoursAgo) * 60 * 60 * 1000
    # получаем текущее время
    currentTime = round(time.time() * 1000)
    # считаем время, с какого считаем PnL
    timeOffset = currentTime - n_miliseconds
    # Connect to an existing database
    engine = get_db_engine()
    # load data from news database
    candlesDf = pd.read_sql(
        "select * from %s where order_time > %d ORDER BY order_time" % (tableName, timeOffset), con=engine)
    return candlesDf


def get_trades_table(symbol, exchange, log, hoursAgo=300):
    '''get trades dataframe from database'''
    tableName = exchange + '_trades_' + symbol.replace("/", "").lower()
    # считаем время для отсечки датафреймов в миллисекундах
    n_miliseconds = int(hoursAgo) * 60 * 60 * 1000
    # получаем текущее время
    currentTime = round(time.time() * 1000)
    # считаем время, с какого считаем PnL
    timeOffset = currentTime - n_miliseconds
    # Connect to an existing database
    # Connect to an existing database
    engine = get_db_engine()
    # load data from news database
    try:
        trades_df = pd.read_sql(
            "select * from %s where time > %d  ORDER BY time" % (tableName, timeOffset), con=engine)
    except:
        trades_df = []
    return trades_df


def get_balances_table(symbol, exchange, log, hoursAgo=300):
    '''get balances dataframe from database'''
    tableName = exchange + '_balances_' + symbol.replace("/", "").lower()
    # считаем время для отсечки датафреймов в миллисекундах
    n_miliseconds = int(hoursAgo) * 60 * 60 * 1000
    # получаем текущее время
    currentTime = round(time.time() * 1000)
    # считаем время, с какого считаем PnL
    timeOffset = currentTime - n_miliseconds
    # Connect to an existing database
    engine = get_db_engine()
    # load data from news database
    try:
        balances_df = pd.read_sql(
            "select * from %s where updatetime > %d ORDER BY updatetime" % (tableName, timeOffset), con=engine)
    except:
        balances_df = []
    return balances_df


# get dataframe with configs from database
def retrieve_configs_table():
    engine = engine = get_db_engine()
    try:
        # get configs from database
        configsDf = pd.read_sql("select * from configs", con=engine)
    except (Exception, pg.Error) as error:
        print(error)
    finally:
        # closing database connection.
        if engine:
            engine.close()
    configsDf = configsDf.reset_index()
    return configsDf