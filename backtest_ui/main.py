import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from models import Strategy
from schemas import Strategy as SchemaStrategy

load_dotenv(".env")

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


@app.get("/")
async def root():
    return {"message": "Welcome to the backtest API"}


@app.post("/strategy", response_model=SchemaStrategy)
def create_strategy(strategy: SchemaStrategy):
    db_strategy = Strategy(
        name=strategy.name,
        buyStakeSize=strategy.buyStakeSize,
        buyWindowSize=strategy.buyWindowSize,
        buyBp=strategy.buyBp,
        buyCooldown=strategy.buyCooldown,
        buyMaxContracts=strategy.buyMaxContracts,
        sellStakeSize=strategy.sellStakeSize,
        sellWindowSize=strategy.sellWindowSize,
        sellBp=strategy.sellBp,
        sellCooldown=strategy.sellCooldown,
        sellMaxContracts=strategy.sellMaxContracts
    )
    db.session.add(db_strategy)
    db.session.commit()
    return db_strategy


@app.get("/strategies/")
def get_strategies():
    return db.session.query(Strategy).all()
