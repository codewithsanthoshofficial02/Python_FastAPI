
from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field
from typing import Optional


# =========================
# Database Model
# =========================
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: int


class CreateUser(SQLModel):
    name: str
    email: str
    phone: int


