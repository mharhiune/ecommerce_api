from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Sample data
products = [
    {"id": 1, "name": "Notepad", "description": "A5 size", "price": 180.0, "image": "Notepad.jpg"},
    {"id": 2, "name": "Phone case", "description": "IPhone", "price": 85.0, "image": "Phone case.jpg"},
    {"id": 3, "name": "Key holder", "description": "Wedding Souvenir", "price": 35.0, "image": "Key holder.jpg"},
]

users = []

carts = {}

# Models
class User(BaseModel):
    id: int
    username: str
    email: str
    password: str

class Login(BaseModel):
    username: str
    password: str

class CartItem(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# Home
@app.get("/")
def home():
    return {"message": "Welcome to RHIUNNE ARTS"}

# Products
@app.get("/products")
def get_products():
    return products

@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# Users
@app.post("/register")
def register(user: User):
    users.append(user.model_dump())
    return {"message": "User registered successfully"}

@app.post("/login")
def login(credentials: Login):
    for user in users:
        if (user["username"] == credentials.username or user["email"] == credentials.username) and user["password"] == credentials.password:
            return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Cart
@app.post("/cart")
def add_to_cart(item: CartItem):
    if item.user_id not in carts:
        carts[item.user_id] = []
    carts[item.user_id].append({"product_id": item.product_id, "quantity": item.quantity})
    return {"message": "Item added to cart"}

@app.get("/cart/{user_id}")
def get_cart(user_id: int):
    return carts.get(user_id, [])

# Checkout
@app.post("/checkout/{user_id}")
def checkout(user_id: int):
    user_cart = carts.get(user_id, [])
    if not user_cart:
        raise HTTPException(status_code=404, detail="Cart is empty or user not found")

    order = []
    total = 0
    for item in user_cart:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        if product:
            subtotal = product["price"] * item["quantity"]
            order.append({
                "product": product["name"],
                "quantity": item["quantity"],
                "price": product["price"],
                "subtotal": subtotal
            })
            total += subtotal

    return {"order": order, "total": total}