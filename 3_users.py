from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

user_details = {
    1: {"name": "santhosh", "email": "santhosh@gmail.com", "phone": 1234567890},
}
user_id = 2


class User(BaseModel):
    name: str
    email: str
    phone: int


@app.post('/users')
async def create_user(user:User):
    global user_id
    user_details[user_id]  = user
    response = {
        "message": "User created successfully",
        "user_id": user_id,
        "user": user_details[user_id]
    }
    user_id += 1
    return response


@app.get('/users')
def get_users():
    return user_details




