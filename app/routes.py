from fastapi import APIRouter, Depends, HTTPException, Body, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .database import SessionLocal
from .models import Account, Transaction, User
from .schemas import TransactionCreate, UserCreate, TokenResponse
from .auth import create_token, verify_password, get_password_hash, decode_token
from jose import JWTError

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")
    token = authorization.split(" ")[1]
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

@router.post("/auth/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Usuário já existe")
    user = User(username=data.username, password_hash=get_password_hash(data.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"username": user.username}

@router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = create_token(user.username)
    return {"access_token": token}

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}

@router.post("/accounts")
async def create_account(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # cria conta para o usuário, caso já não exista
    result = await db.execute(select(Account).where(Account.owner == current_user.username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Conta já existe para o usuário")
    account = Account(owner=current_user.username, balance=0.0)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return {"id": account.id, "owner": account.owner, "balance": account.balance}

@router.get("/accounts")
async def list_accounts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.owner == current_user.username))
    accounts = result.scalars().all()
    return [{"id": a.id, "owner": a.owner, "balance": a.balance} for a in accounts]

@router.get("/accounts/{account_id}")
async def get_account(account_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account or account.owner != current_user.username:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    return {"id": account.id, "owner": account.owner, "balance": account.balance}

@router.post("/accounts/{account_id}/transactions")
async def create_transaction(account_id: int, data: TransactionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Valor inválido")
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account or account.owner != current_user.username:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    if data.type == "withdraw" and account.balance < data.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")
    if data.type == "deposit":
        account.balance += data.amount
    else:
        account.balance -= data.amount
    transaction = Transaction(type=data.type, amount=data.amount, account_id=account_id)
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return {"message": "Transação realizada com sucesso", "transaction": {"id": transaction.id, "type": transaction.type, "amount": transaction.amount, "timestamp": transaction.timestamp.isoformat()}, "balance": account.balance}

@router.get("/accounts/{account_id}/statement")
async def statement(account_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    if not account or account.owner != current_user.username:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    result = await db.execute(select(Transaction).where(Transaction.account_id == account_id))
    return [{"id": t.id, "type": t.type, "amount": t.amount, "timestamp": t.timestamp.isoformat()} for t in result.scalars().all()]