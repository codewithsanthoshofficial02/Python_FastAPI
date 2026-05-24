from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Session

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q} 

@app.post("/items/")
async def create_item(name: str, price: float):
    return {"name": name, "price": price}

@app.put("/items/{item_id}")
async def update_item(item_id: int, name: str = None, price: float = None):
    return {"item_id": item_id, "name": name, "price": price}  



users = {
    1: {"name": "santhosh",
        "orders": [
            {"id": 1, "item": "Laptop", "price": 1200},
            {"id": 2, "item": "Phone", "price": 800}
        ]
    },
    2: {"name": "Kumar",
        "orders": [
            {"id": 3, "item": "Tablet", "price": 600}
        ]
    },
    3: {"name": "Koneti",
        "orders": [
            {"id": 4, "item": "Watch", "price": 300}
        ]
    }
}

@app.get('/user/{user_id}')
async def get_user(user_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users.get(user_id)



@app.get('/user/{user_id}/order/{order_id}')
async def get_user_order(user_id: int, order_id: int):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    elif order_id < 1 or order_id > len(users.get(user_id).get("orders")):
        raise HTTPException(status_code=404, detail="Order not found")
    return users.get(user_id).get("orders")[order_id-1]





