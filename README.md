# zagrava interview
During this technical assignment you would need to design and implement a backtesting system. For the purpose of this assignment we will limit our system to Binance USD(S)-M futures. This system would need to consist of 4 parts:
 ⁃ Data collection unit that would gather 1 minute candles in the specified range.
 ⁃ User-defined strategy, a minimalistic interface in which the user can specify the conditions in which he or she will buy or sell. 
 ⁃ Processing unit that would, given the collected data and user strategy, would calculate PnL (realized + unrealized) during each 1min period.
 ⁃ Analysis unit that would calculate final PnL, Sharpe ratio, drawdown, and display them to the user alongside with PnL graph
