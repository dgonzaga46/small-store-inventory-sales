Small Store Inventory and Sales System

Project Overview
The Small Store Inventory and Sales System is a simple information system developed using Python and FastAPI. It helps small store owners manage their products, check available stocks, and record sales transactions in an organized way.

Problem Statement
Managing products and sales manually can be difficult, especially when keeping track of available stocks and calculating the total amount of each sale. This system helps solve these problems by storing product information in a database and automatically updating the stock whenever a sale is recorded.

Main Features
Add new products to the inventory.
View the list of products and their details.
Update product information, such as price and stock quantity.
Delete products that have no existing sale records.
Record sales transactions and calculate the total amount.
Automatically deduct sold quantities from the available stock.
Prevent sales when the requested quantity exceeds the available stock.
Database
The system uses SQLite and has three related tables:
Products – stores the product name, price, and available stock.
Sales – stores the date and total amount of each sale.
Sale Items – records the products and quantities included in each sale.
Primary keys identify each record, while foreign keys connect the related tables.

Technologies Used
Python
FastAPI
SQLite
Pydantic
Uvicorn

How to Run the Project
Install Python on your computer.
Open a terminal in the project folder.
Install the required packages:
python -m pip install -r requirements.txt
Run the application:
python -m uvicorn main:app --reload

Open the following link in your browser to view and test the API endpoints:
http://127.0.0.1:8000/docs

GitHub Repository
https://github.com/dgonzaga46/small-store-inventory-sales


