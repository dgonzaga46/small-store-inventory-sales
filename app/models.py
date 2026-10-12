
"""Models for the Small Store Inventory and Sales System."""

from datetime import date

from pydantic import BaseModel, Field


class ProductInput(BaseModel):
    """Fields required to create or update a product."""

    name: str = Field(min_length=1)
    price: float = Field(ge=0)
    stock_quantity: int = Field(ge=0)


class Product(ProductInput):
    """A product record returned by the API."""

    id: int


class SaleItemInput(BaseModel):
    """A product and quantity included in a sale."""

    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class SaleInput(BaseModel):
    """Products included in one sale."""

    items: list[SaleItemInput] = Field(min_length=1)


class SaleItem(BaseModel):
    """An item belonging to a sale."""

    id: int
    sale_id: int
    product_id: int
    quantity: int
    unit_price: float


class Sale(BaseModel):
    """A completed sale record."""

    id: int
    sale_date: str
    total_amount: float
    items: list[SaleItem] = Field(default_factory=list)


class StoreOperations:
    """Database operations for products and sales."""

    @staticmethod
    def list_products(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, price, stock_quantity "
                "FROM products ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_product(product_id, database_connection):
        with database_connection() as connection:
            row = connection.execute(
                "SELECT id, name, price, stock_quantity "
                "FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def create_product(product_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO products (name, price, stock_quantity) "
                "VALUES (?, ?, ?)",
                (
                    product_input.name,
                    product_input.price,
                    product_input.stock_quantity,
                ),
            )
            row = connection.execute(
                "SELECT id, name, price, stock_quantity "
                "FROM products WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(row)

    @staticmethod
    def update_product(product_id, product_input, database_connection):
        with database_connection() as connection:
            connection.execute(
                "UPDATE products SET name = ?, price = ?, stock_quantity = ? "
                "WHERE id = ?",
                (
                    product_input.name,
                    product_input.price,
                    product_input.stock_quantity,
                    product_id,
                ),
            )
            row = connection.execute(
                "SELECT id, name, price, stock_quantity "
                "FROM products WHERE id = ?",
                (product_id,),
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete_product(product_id, database_connection):
        with database_connection() as connection:
            connection.execute(
                "DELETE FROM products WHERE id = ?",
                (product_id,),
            )

    @staticmethod
    def list_sales(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                "SELECT id, sale_date, total_amount FROM sales ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_sale(sale_id, database_connection):
        with database_connection() as connection:
            sale = connection.execute(
                "SELECT id, sale_date, total_amount "
                "FROM sales WHERE id = ?",
                (sale_id,),
            ).fetchone()

            if sale is None:
                return None

            items = connection.execute(
                "SELECT id, sale_id, product_id, quantity, unit_price "
                "FROM sale_items WHERE sale_id = ?",
                (sale_id,),
            ).fetchall()

        return {
            **dict(sale),
            "items": [dict(item) for item in items],
        }

    @staticmethod
    def create_sale(sale_input, database_connection):
        with database_connection() as connection:
            total_amount = 0.0
            prepared_items = []
            requested_quantities = {}

            # Check all requested quantities, including duplicate product IDs.
            for item in sale_input.items:
                requested_quantities[item.product_id] = (
                    requested_quantities.get(item.product_id, 0)
                    + item.quantity
                )

            # Validate stock and prepare the sale items.
            for product_id, total_quantity in requested_quantities.items():
                product = connection.execute(
                    "SELECT id, price, stock_quantity "
                    "FROM products WHERE id = ?",
                    (product_id,),
                ).fetchone()

                if product is None:
                    raise ValueError(
                        f"Product {product_id} does not exist."
                    )

                if product["stock_quantity"] < total_quantity:
                    raise ValueError(
                        f"Not enough stock for product {product_id}."
                    )

            for item in sale_input.items:
                product = connection.execute(
                    "SELECT id, price FROM products WHERE id = ?",
                    (item.product_id,),
                ).fetchone()

                unit_price = product["price"]
                total_amount += unit_price * item.quantity
                prepared_items.append(
                    (item.product_id, item.quantity, unit_price)
                )

            # Create the sale record.
            cursor = connection.execute(
                "INSERT INTO sales (sale_date, total_amount) VALUES (?, ?)",
                (date.today().isoformat(), round(total_amount, 2)),
            )
            sale_id = cursor.lastrowid

            # Record sale items and deduct stock.
            for product_id, quantity, unit_price in prepared_items:
                connection.execute(
                    "INSERT INTO sale_items "
                    "(sale_id, product_id, quantity, unit_price) "
                    "VALUES (?, ?, ?, ?)",
                    (sale_id, product_id, quantity, unit_price),
                )

                connection.execute(
                    "UPDATE products SET stock_quantity = "
                    "stock_quantity - ? WHERE id = ?",
                    (quantity, product_id),
                )

        # Return the sale only after the transaction commits.
        return StoreOperations.get_sale(sale_id, database_connection)
