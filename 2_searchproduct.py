from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Laptop", "price": 999, "category": "Electronics"},
    {"id": 2, "name": "Phone", "price": 499, "category": "Electronics"},
    {"id": 3, "name": "Tablet", "price": 299, "category": "Electronics"},
    {"id": 4, "name": "Headphones", "price": 199, "category": "Electronics"},
    {"id": 5, "name": "Notebook", "price": 9.99, "category": "Stationery"},
    {"id": 6, "name": "Pen", "price": 1.99, "category": "Stationery"},
    {"id": 7, "name": "Backpack", "price": 49.99, "category": "Accessories"},
    {"id": 8, "name": "Watch", "price": 199.99, "category": "Accessories"},
    {"id": 9, "name": "Shoes", "price": 79.99, "category": "Footwear"},
    {"id": 10, "name": "Jacket", "price": 149.99, "category": "Clothing"}
]


@app.get('/products')
async def search_products(category: Optional[str]=None, max_price: Optional[float] = None):
    results = products
    if category:
        results = [product for product in results if product["category"].lower() == category.lower()]
    if max_price:
        results = [product for product in results if product["price"] <= max_price]

    return results
