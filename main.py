from fastapi import FastAPI
from products import products

app = FastAPI()

@app.get("/")
def get_home():
    return {"message": "Welcome to our E-commerce API"}

#list of sample products
@app.get("/products")
def get_products():
    return {"products": products}

@app.get("/products{product_id}")
def get_product_by_id(product_id: int):
    # return {"product_id": product_id}
    for product in products:
        if product["id"] == product_id:
            return {"products": products}