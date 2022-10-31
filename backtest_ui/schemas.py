from pydantic import BaseModel

class Strategy(BaseModel):
    name: str
    windowSize: int
    buyStakeSize: int
    buyBp: int
    buyCooldown: int
    buyMaxContracts: int
    sellStakeSize: int
    sellBp: int
    sellCooldown: int
    sellMinContracts: int

    class Config:
        orm_mode = True