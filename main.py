from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import products_collection
from db import carts_collection
from db import users_collection
from bson.objectid import ObjectId
from utils import replace_mongo_id


# Models
class ProductModel(BaseModel):
    name: str
    stock_quantity: int
    description: str
    price: float

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

class Login(BaseModel):
    email: str
    password: str

class Item(BaseModel):
    email: str
    product_id: str

class CartItem(BaseModel):
    item: Item
    quantity: int

app = FastAPI()

# Home
@app.get("/")
def home():
    return {"message": "Welcome to RHIUNNE ARTS"}

# Products
@app.get("/products")
def get_products():
    products = list(products_collection.find())
    return {"data": list(map(replace_mongo_id, products))}

@app.get("/products/{product_id}")
def get_product(product_id: str):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return replace_mongo_id(product)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    
# Users
@app.post("/register")
def register(user: RegisterUser):
    existing_user = users_collection.find_one({
        "$or": [{"email": user.email}, {"username": user.username}]
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one(user.dict())
    return {"message": "User registered successfully"}

@app.post("/login")
def login(credentials: Login):
    user = users_collection.find_one({
        "email": credentials.email,
        "password": credentials.password  # Insecure: use hashed passwords in production
    })

    if user:
        return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Add to Cart
@app.post("/cart")
def add_to_cart(item: CartItem):
    try:
        product = products_collection.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Add or update cart item
        existing = carts_collection.find_one({
            "email": item.email,
            "product_id": item.product_id
        })

        if existing:
            # Update quantity
            new_quantity = existing["quantity"] + item.quantity
            carts_collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"quantity": new_quantity}}
            )
        else:
            # Insert new cart item
            carts_collection.insert_one(item.dict())

        return {"message": "Item added to cart"}

    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product ID format")

# Get Cart
@app.get("/cart/{email}")
def get_cart(email: str):
    cart_items = list(carts_collection.find({"email": email}))
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty or user not found")

    for item in cart_items:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            item["product_details"] = replace_mongo_id(product)

    return {"cart": list(map(replace_mongo_id, cart_items))}

# Checkout
@app.post("/checkout/{email}")
def checkout(email: str):
    cart_items = list(carts_collection.find({"email": email}))
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty or user not found")

    order = []
    total = 0

    for item in cart_items:
        try:
            product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
            if product:
                quantity = item["quantity"]
                subtotal = product["price"] * quantity

                order.append({
                    "product": product["name"],
                    "quantity": quantity,
                    "price": product["price"],
                    "subtotal": subtotal
                })

                total += subtotal
        except Exception:
            continue  # skip invalid products

    # Clear the cart after checkout
    carts_collection.delete_many({"email": email})

    return {"order": order, "total": total}