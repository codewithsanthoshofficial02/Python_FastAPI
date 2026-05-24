from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI()

user_details = {}
user_id = 1


class User(BaseModel): 
    name: str = Field(..., min_length=2, max_length=20)
    phone: int = Field(..., ge=0, le=10000000000)
    email: str


@app.post('/create_user')
async def create_user(user: User):
    global user_id
    user_details[user_id] = user
    response = {
        "message": "User created successfully",
        "user_id": user_id,
        "user": user_details[user_id]
    }
    user_id += 1
    return response

@app.get('/users')
async def get_users():
    if not user_details:
        raise HTTPException(status_code=404, detail="No users found")
    return user_details

@app.get('/user/{user_id}')
async def get_user(user_id: int):
    if user_id not in user_details:
        raise HTTPException(status_code=404, detail="User not found")
    return user_details[user_id]

@app.put("/user/{user_id}")
async def update_user(user_id:int, user:User):
    if user_id not in user_details:
        raise HTTPException(status_code=404, detail = "User not found")
    user_details[user_id] = user
    return {"message":"User updated", "user":user}

@app.delete("/user/{user_id}")
async def delete_user(user_id:int):
    if user_id not in user_details:
        raise HTTPException(status_code=404, detail = "User not found")
    delete = user_details.pop(user_id)
    return {"message": "User deleted", "user":delete}









