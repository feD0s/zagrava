from pydantic import BaseModel

class Strategy(BaseModel):
    name: str
    buyStakeSize: int
    buyWindowSize: int
    buyBp: int
    buyCooldown: int
    buyMaxContracts: int
    sellStakeSize: int
    sellWindowSize: int
    sellBp: int
    sellCooldown: int
    sellMaxContracts: int

    class Config:
        orm_mode = True