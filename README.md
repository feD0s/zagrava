# Zagrava interview task
During this technical assignment you would need to design and implement a backtesting system. For the purpose of this assignment we will limit our system to Binance USD(S)-M futures. This system would need to consist of 4 parts:<br/>
 ⁃ Data collection unit that would gather 1 minute candles in the specified range.<br/>
 ⁃ User-defined strategy, a minimalistic interface in which the user can specify the conditions in which he or she will buy or sell.<br/>
 ⁃ Processing unit that would, given the collected data and user strategy, would calculate PnL (realized + unrealized) during each 1min period.<br/>
 ⁃ Analysis unit that would calculate final PnL, Sharpe ratio, drawdown, and display them to the user alongside with PnL graph<br/>
 
 # Solution

## 1. Solution analysis in jupyter notebook

In 'notebook' folder there's file 'notebook.pynb' with simple solution. User strategy can be adjusted in 'strategy.yaml' and you also can change some parameters in 'config.yaml'.

## 2. Service structure

After running docker-compose 4 counteiners will be built:<br/>
1) postgresql_db - local postgres database for storing user strategies</br>
2) pgadmin for viewing created tables</br>
3) backtest_ui - web service where users can list, create, retrieve, update and delete user strategies. Service is made via FastAPI and React</br>
4) telegram_pnl - telegram bot where users can run commands to backtest strategies

## 3. Backtesting workflow

1) User runs web service and creates strategies</br>
   ![fastAPI Swagger UI](https://github.com/feD0s/zagrava/blob/main/fastapi.png?raw=true)
   
3) User runs telegram bot and backtests created strategies 
