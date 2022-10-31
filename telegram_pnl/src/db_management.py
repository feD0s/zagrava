import os

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


def check_table(tableName, log):
    '''check if table exists in database'''
    try:
        # Connect to an existing database
        engine = get_db_engine()
        cursor = engine.cursor()
        # check if database exists
        cursor.execute(
            "select exists(select * from information_schema.tables where table_name=%s)", (tableName,))
        result = cursor.fetchone()[0]
        if result == True:
            log.debug('Table exists')
        else:
            log.debug("Table doesn't exist")
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


def get_table(tableName, log):
    '''get table from database'''
    # Connect to an existing database
    engine = get_db_engine()
    # load data from news database
    try:
        df = pd.read_sql(
            "select * from %s" % (tableName), con=engine)
    except:
        df = []
        log.debug('No strategies has been found')
    finally:
        if engine:
            engine.close()
            log.debug("PostgreSQL connection is closed")
        return df