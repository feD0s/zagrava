# Zagrava interview task
During this technical assignment you would need to design and implement a backtesting system. For the purpose of this assignment we will limit our system to Binance USD(S)-M futures. This system would need to consist of 4 parts:<br/>
 ⁃ Data collection unit that would gather 1 minute candles in the specified range.<br/>
 ⁃ User-defined strategy, a minimalistic interface in which the user can specify the conditions in which he or she will buy or sell.<br/>
 ⁃ Processing unit that would, given the collected data and user strategy, would calculate PnL (realized + unrealized) during each 1min period.<br/>
 ⁃ Analysis unit that would calculate final PnL, Sharpe ratio, drawdown, and display them to the user alongside with PnL graph<br/>
 
 # Solution

## 1. Solution analysis in jupyter notebook

In 'notebook' folder there's file 'notebook.pynb' with simple solution. User strategy can be adjusted in 'strategy.yaml' and you also can change some parameters in 'config.yaml'.

![Jupyter Notebook](https://github.com/feD0s/zagrava/blob/main/notebook/notebook.ipynb)

## 2. Service structure

After running docker-compose 4 counteiners will be built:<br/>
1) postgresql_db - local postgres database for storing user strategies</br>
2) pgadmin for viewing created tables</br>
3) backtest_ui - web service where users can create user strategies. Service is made via FastAPI and React</br>
4) telegram_pnl - telegram bot where users can run commands to backtest strategies

## 3. Backtesting workflow

1) User runs web service and creates strategies</br>
   ![fastAPI Swagger UI](https://github.com/feD0s/zagrava/blob/main/fastapi.png?raw=true)
   ![React UI](https://github.com/feD0s/zagrava/blob/main/React%20UI.png?raw=true)
3) User runs telegram bot and backtests created strategies 
   ![telegram UI](https://github.com/feD0s/zagrava/blob/main/telegram%20UI.png?raw=true)

# How to run
Disclamer: I removed .env files from .gitignore on purpose. I know that it's not secure but for this task I find it acceptable.
## 1. Intall Docker
To install docker on your system please follow official documentation:</br>
https://docs.docker.com/get-docker/
## 2. Clone git repository
1) create empty folder</br>
2) open folder in terminal</br>
3) clone git repository - run command: git clone https://github.com/feD0s/zagrava.git
## 3. Run docker compose
1) open folder "zagrava": cd zagrava</br>
2) run docker compose: docker-compose up --build</br>
Sometimes I got i/o errors while building docker compose. In this case I just run "docker-compose up --build" again.
## 4. Migrate schemas to database
We need this action to create database tables.</br>
1) open new terminal window and view all running containers: docker ps</br>
2) copy containter ID of zagrava_backand image</br>
3) run commands to create tables:</br>
docker exec -it %CONTAINER_ID% alembic revision --autogenerate -m "New Migration"</br>
docker exec -it %CONTAINER_ID% alembic upgrade head</br>
## 5. Using the service
### Frontend
open http://127.0.0.1:3000/ to create or delete strategies</br>
### API Docs
you can view API docs here in swagger format http://127.0.0.1:8000/docs or if you prefer Redoc: http://127.0.0.1:8000/redoc#tag/main-page</br>
### PG Admin
To view created tables in pgadmin visit http://127.0.0.1:5050</br>
login: fazarov@gmail.com</br>
password: admin</br>
then connect to database: Object -> Register -> Server</br>
General Tab: Name: db</br>
Connection Tab: </br>
Host name: db</br>
Port: 5432</br>
Maintenance database: backtest</br>
Username: backtester</br>
Password: backtester</br>
Now you can view created table "strategy" in Servers -> DB -> Databases -> Backtest -> Schemas -> public -> Tables</br>
### Telegram backtesting
After you created strategy you can backtest it in telegram</br>
1) Open telegram, find @zagrava_backtest_bot
2) Type /start
3) backtest %STRATEGY_NAME%
