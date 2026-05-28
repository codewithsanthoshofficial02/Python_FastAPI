from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select, create_engine
from contextlib import asynccontextmanager
from typing import Annotated
from pathlib import Path
from JWTModel import User, CreateUser, LoginUser, TokenData
import os, shutil
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 


# ================================================================  
# DB Setup - session 
# ================================================================  

# Absolute path to project directory
BASE_DIR = Path(__file__).resolve().parent
# SQLite database file
DATABASE_URL = f"sqlite:///{BASE_DIR}/users.db"
# Database engine
engine = create_engine(DATABASE_URL, echo=True)


# App Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    SQLModel.metadata.create_all(bind=engine)
    print(f"Database file location: {BASE_DIR / 'users.db'}")
    print(Path("users.db").resolve())
    yield


# FastAPI app
app = FastAPI(lifespan=lifespan)


# Session Dependency
def get_session():
    with Session(engine) as session:
        yield session


SessionDep =  Annotated[Session, Depends(get_session)]

# ================================================================  
#JWT setup: pip install "python-jose[cryptography]" 
# ================================================================  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRECT_KEY = "mysecrectkey"
ALGORITHEM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRECT_KEY, algorithm=ALGORITHEM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRECT_KEY, algorithms=[ALGORITHEM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    email = verify_access_token(token)
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user




# ================================================================  
#Auth
# ================================================================ 
def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ================================================================ 
# Methods Register, Login
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


@app.post("/login", response_model=TokenData)
def login(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):

    user = session.exec( select(User).where(User.email == form_data.username)).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")

    pwd = verify_password( form_data.password, user.hashed_password)

    if not pwd:
        raise HTTPException( status_code=400, detail="Invalid Credentials")

    access_token = create_access_token(data={"sub": user.email})
    return TokenData(access_token=access_token, token_type="bearer")





@app.get("/profile")
def get_profile(current_user:Annotated[User, Depends(get_current_user)]):
    return {"message": f"Welcome {current_user.name}!", "email": current_user.email}
# ================================================================ 