"""FastAPI endpoints for the Small Store Inventory and Sales System."""

import sqlite3

from fastapi import FastAPI, HTTPException

from app.database import database_connection, initialize_database
from app.models import ProductInput, SaleInput, StoreOperations

app = FastAPI(title="Small Store Inventory and Sales System")


@app.get("/")
def home():
    return {
        "message": "Welcome to the Small Store Inventory and Sales System!",
        "docs": "/docs",
    }


# PRODUCT ENDPOINTS


@app.get("/products")
def get_products():
    return {"products": StoreOperations.list_products(database_connection)}


@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = StoreOperations.get_product(product_id, database_connection)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"product": product}


@app.post("/products", status_code=201)
def create_product(product: ProductInput):
    return {
        "product": StoreOperations.create_product(
            product, database_connection
        )
    }


@app.put("/products/{product_id}")
def edit_product(product_id: int, product: ProductInput):
    updated = StoreOperations.update_product(
        product_id, product, database_connection
    )

    if updated is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"product": updated}


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    try:
        StoreOperations.delete_product(product_id, database_connection)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a product that has sale records",
        )

    return {"message": "Product deleted successfully"}


# SALES ENDPOINTS


@app.get("/sales")
def get_sales():
    return {"sales": StoreOperations.list_sales(database_connection)}


@app.get("/sales/{sale_id}")
def get_sale(sale_id: int):
    sale = StoreOperations.get_sale(sale_id, database_connection)

    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")

    return {"sale": sale}


@app.post("/sales", status_code=201)
def create_sale(sale: SaleInput):
    try:
        result = StoreOperations.create_sale(sale, database_connection)
        return {"sale": result}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


initialize_database()
