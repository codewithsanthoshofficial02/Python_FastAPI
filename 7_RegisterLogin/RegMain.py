from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select, create_engine
from contextlib import asynccontextmanager
from typing import Annotated
from pathlib import Path
from RegModel import User, CreateUser, LoginUser
import os, shutil
import bcrypt



# Absolute path to project directory
BASE_DIR = Path(__file__).resolve().parent

# SQLite database file
DATABASE_URL = f"sqlite:///{BASE_DIR}/users.db"

# Database engine
engine = create_engine(DATABASE_URL, echo=True)


# =========================
# App Lifespan
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    SQLModel.metadata.create_all(bind=engine)
    print(f"Database file location: {BASE_DIR / 'users.db'}")
    print(Path("users.db").resolve())
    yield


# FastAPI app
app = FastAPI(lifespan=lifespan)


# =========================
# Session Dependency
# =========================
def get_session():
    with Session(engine) as session:
        yield session


SessionDep =  Annotated[Session, Depends(get_session)]


# ================================================================ Auth

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# def hash_password(password:str) -> str :
#     return pwd_context.hash(password)

# def verify_password(plain:str, hashed:str) -> bool :
#     return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ================================================================


@app.post("/register")
def register(session: SessionDep, user_data: CreateUser):
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hash_pwd = hash_password(user_data.password)

    # Create new user
    new_user = User(email = user_data.email, name = user_data.name, hashed_password = hash_pwd)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user}
    # return {"message": "User registered successfully", "user_id": new_user.id}


@app.post("/login")
def login(session: SessionDep, login_user: LoginUser):

    user = session.exec( select(User).where(User.email == login_user.email)).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    pwd = verify_password( login_user.password, user.hashed_password)

    if not pwd:
        raise HTTPException( status_code=400, detail="Invalid Credentials")

    return user

