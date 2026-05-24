from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Session, select, create_engine
from contextlib import asynccontextmanager
from typing import Annotated
from pathlib import Path
from RegModel import User, CreateUser, LoginUser
from pathlib import Path
from FileModel import User, CreateUser
import os, shutil



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







