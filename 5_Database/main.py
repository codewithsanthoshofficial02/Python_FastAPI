from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Annotated
from contextlib import asynccontextmanager
from pathlib import Path
from models import User, CreateUser

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



# =========================
# Test Route
# =========================
@app.get("/")
def root():
    return {"message": "FastAPI + SQLModel + SQLite working"}



@app.post("/create_user")
def create_new_user(user: CreateUser, session: SessionDep):
    # db_user = User(**user.dict())
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.get("/users", response_model=list[User])
def get_users(session: SessionDep):
    users = session.exec(select(User)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users


@app.get('/user/{user_id}', response_model=User)
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/user/{user_id}", response_model=User)
def update_user(user_id: int, user: CreateUser, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Update fields
    db_user.name = user.name
    db_user.email = user.email
    db_user.phone = user.phone
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user



@app.delete("/user/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
