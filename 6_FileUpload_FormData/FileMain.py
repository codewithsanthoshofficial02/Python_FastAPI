from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from sqlmodel import SQLModel, create_engine, Session, select
from contextlib import asynccontextmanager
from typing import Annotated
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


# =========================
# Create upload folder: uploads
# =========================

UPLOADS_DIRS = "uploads"
os.makedirs(UPLOADS_DIRS, exist_ok=True)

# =========================
# Create User
# =========================

@app.post("/createuser")
def usercreate(
    session:SessionDep,
    name:str = Form(...),
    phone:int = Form(...),
    email:str = Form(),
    file:UploadFile = File(...),
    ):

    user_data = { "name":name, "phone":phone, "email":email }
    validated = CreateUser.model_validate(user_data)

    file_path = os.path.join(UPLOADS_DIRS, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    #. ** it means again converted validated model to dictionary format.  (user_data-> Dic, validated -> Model, ** -> again return back Dic)
    # user = User(**validated.model_dump(), file_path=file.filename)
    user = User(**validated.model_dump(), file_path=f'{UPLOADS_DIRS}/{file.filename}')

    session.add(user)
    session.commit()
    session.refresh(user)
    return user




































