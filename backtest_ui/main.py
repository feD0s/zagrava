import os
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, status
from fastapi_sqlalchemy import DBSessionMiddleware, db

from models import Strategy
from schemas import Strategy as SchemaStrategy

load_dotenv(".env")

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


@app.get("/")
async def root():
    return {"message": "Welcome to the backtest API"}


@app.get("/strategy/", response_model=List[SchemaStrategy], tags=["strategy"])
def get_strategies():
    return db.session.query(Strategy).all()


@app.post("/strategy/", response_model=SchemaStrategy, status_code=status.HTTP_201_CREATED, tags=["strategy"])
def create(strategy: SchemaStrategy):
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


@app.get("/strategy/{name}", response_model=SchemaStrategy, status_code=status.HTTP_200_OK, tags=["strategy"])
def retrieve(name: str):
    strategy = db.session.query(Strategy).filter(Strategy.name == name).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    return strategy


@app.put("/strategy/{name}", status_code=status.HTTP_200_OK, tags=["strategy"])
def update(name: str, strategy: SchemaStrategy):
    db_strategy = db.session.query(Strategy).filter(Strategy.name == name).first()
    if not db_strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    db_strategy.name=strategy.name,
    db_strategy.buyStakeSize=strategy.buyStakeSize,
    db_strategy.buyWindowSize=strategy.buyWindowSize,
    db_strategy.buyBp=strategy.buyBp,
    db_strategy.buyCooldown=strategy.buyCooldown,
    db_strategy.buyMaxContracts=strategy.buyMaxContracts,
    db_strategy.sellStakeSize=strategy.sellStakeSize,
    db_strategy.sellWindowSize=strategy.sellWindowSize,
    db_strategy.sellBp=strategy.sellBp,
    db_strategy.sellCooldown=strategy.sellCooldown,
    db_strategy.sellMaxContracts=strategy.sellMaxContracts
    db.session.commit()
    return 'the strategy was updated successfully'

@app.delete('/strategy/{name}', status_code=status.HTTP_204_NO_CONTENT, tags=["strategy"])
def delete(name: str):
    strategy = db.session.query(Strategy).filter(Strategy.name == name).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    db.session.delete(strategy)
    db.session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
