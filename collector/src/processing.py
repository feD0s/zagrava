import pandas as pd

msec = 1000
minute = 60 * msec
hold = 30

# pnl calculation algorithm was taken from:
# https://www.tradingtechnologies.com/xtrader-help/fix-adapter-reference/pl-calculation-algorithm/understanding-pl-calculations/?cn-reloaded=1
def get_pnlDf(strat: dict, comissionRate: float, candlesDf: pd.DataFrame) -> pd.DataFrame:
    """Returns two dataframes with pnl and trades based on the strategy parameters and candles dataframe"""
    buyStakeSize = strat['buyStakeSize']
    buyBp = strat['buyBp']
    buyCooldown = strat['buyCooldown']
    buyMaxContracts = strat['buyMaxContracts']
    sellStakeSize = strat['sellStakeSize']
    sellBp = strat['sellBp']
    sellCooldown = strat['sellCooldown']
    sellMinContracts = strat['sellMinContracts']
    lastBuyTradeTime = 0
    lastSellTradeTime = 0
    pnlRealized = 0
    pnlUnrealized = 0
    position = 0
    averageOpenPrice = 0
    pnlUnrealized = 0
    pnlTotal = 0
    comissionTotal = 0

    # create empty dataframe
    pnlDf = pd.DataFrame(columns=['updatetime', 'close', 'pnlRealized',
                         'pnlUnrealized', 'pnlTotal', 'comissionTotal', 'position', 'averageOpenPrice'])

    # for each candle calculate pnl and trades
    for index, row in candlesDf.iterrows():
        # of price is lower then ma, if position will not get grater then we specified and if cooldown is over
        if row['close'] * (1 + buyBp / 10000) < row['ma'] and \
                position + buyStakeSize <= buyMaxContracts and \
                row['updatetime'] - lastBuyTradeTime > buyCooldown * minute:
            # update lastBuyTradeTime and timeSinceLastBuyTrade
            timeSinceLastBuyTrade = (
                row['updatetime'] - lastBuyTradeTime) / minute
            lastBuyTradeTime = row['updatetime']
            # calculate comission
            comissionTotal += buyStakeSize * row['close'] * comissionRate
            # if position was >= 0 then new buy fills will not affect realized pnl
            # but will affect unrealized pnl and total pnl
            if position >= 0:
                averageOpenPrice = (averageOpenPrice * position + row['close'] * buyStakeSize) / \
                    (position + buyStakeSize)
                position += buyStakeSize
            # if position was < 0 then new buy fills will affect realized pnl, unrealized pnl and total pnl
            elif position < 0:
                pnlRealized += (averageOpenPrice - row['close']) * \
                    min(buyStakeSize, -position)
                position += buyStakeSize
                # if position is still negative averageOpenPrice will not change
                # if position becomes 0 averageOpenPrice will be also 0
                # if position becomes positive averageOpenPrice will be equal to row['close']
                if position == 0:
                    averageOpenPrice = 0
                elif position > 0:
                    averageOpenPrice = row['close']

        elif row['close'] * (1 - sellBp / 10000) >= row['ma'] and \
                position - sellStakeSize > sellMinContracts and \
                row['updatetime'] - lastSellTradeTime > sellCooldown * minute:
            timeSinceLastSellTrade = (
                row['updatetime'] - lastSellTradeTime) / minute
            lastSellTradeTime = row['updatetime']
            # calculate comission
            comissionTotal += sellStakeSize * row['close'] * comissionRate
            # if position < 0 then new sell fills will not affect realized pnl
            # but will affect unrealized pnl and total pnl
            if position <= 0:
                averageOpenPrice = (averageOpenPrice * abs(position) + row['close'] * sellStakeSize) / \
                    (abs(position) + sellStakeSize)
                position -= sellStakeSize

            # if position > 0 then new sell fills will affect realized pnl, unrealized pnl and total pnl
            elif position > 0:
                pnlRealized += (row['close'] - averageOpenPrice) * \
                    min(sellStakeSize, position)
                position -= sellStakeSize
                # if position is still positive averageOpenPrice will not change
                # if position becomes 0 averageOpenPrice will be also 0
                # if position becomes negative averageOpenPrice will be equal to row['close']
                if position == 0:
                    averageOpenPrice = 0
                elif position < 0:
                    averageOpenPrice = row['close']
        # update pnlUnrealized and pnlTotal for each candle
        pnlUnrealized = (row['close'] - averageOpenPrice) * position
        pnlTotal = pnlRealized + pnlUnrealized
        # add row to pnlDf
        pnlDf = pnlDf.append({
            'updatetime': row['updatetime'],
            'close': row['close'],
            'pnlRealized': pnlRealized,
            'pnlUnrealized': pnlUnrealized,
            'pnlTotal': pnlTotal,
            'comissionTotal': comissionTotal,
            'position': position,
            'averageOpenPrice': averageOpenPrice
        }, ignore_index=True)
    # add pnlFinal column which shows totalPnl with taking comission into account
    pnlDf['pnlFinal'] = pnlDf['pnlTotal'] - pnlDf['comissionTotal']
    return pnlDf
