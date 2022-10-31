import math

def get_sharpeRatio(pnlDf, tradingDaysCount, riskFreeRate):
    # calculate sharpe ratio
    pnlDf['dailyReturn'] = pnlDf['close'].pct_change()
    dailyReturnMean = pnlDf['dailyReturn'].mean()
    dailyReturnStd = pnlDf['dailyReturn'].std()
    sharpeRatio = (dailyReturnMean - riskFreeRate /
                   tradingDaysCount) / dailyReturnStd
    # calculate annualized sharpe ratio
    annualizedSharpeRatio = sharpeRatio * math.sqrt(tradingDaysCount)
    return annualizedSharpeRatio


# function to calculate maximum drawdown in percent
def get_maxDrawdown(pnlDf):
    if pnlDf.pnlFinal.iloc[-1] == 0:
        return 0
    pnlDf['drawdown'] = pnlDf['pnlFinal'].cummax() - pnlDf['pnlFinal']
    maxDrawdown = pnlDf['drawdown'].max()
    maxDrawdownPercent = maxDrawdown / pnlDf['pnlFinal'].cummax().max() * 100
    return maxDrawdownPercent
