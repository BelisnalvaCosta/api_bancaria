from pydantic import BaseModel

class TransactionCreate(BaseModel):
    type: str
    amount: float

class TransactionResponse(BaseModel):
    type: str
    amount: float
    timestamp: str

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str