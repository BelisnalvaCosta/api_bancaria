from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    owner = Column(String, unique=True)
    balance = Column(Float, default=0.0)
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    type = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="transactions")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)