"""
seed_data.py
Generates realistic sample retail data for the Inventory Management System.
Run this once to populate products, purchases (stock-in history), and sales
(stock-out history) with data spread across the last 6 months — enough to
support meaningful trend analysis (best sellers, slow movers, turnover, etc.)

Usage:
    python seed_data.py
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "inventory.db"

# ---- 1. Sample product catalog (general retail: electronics, groceries, household) ----
PRODUCTS = [
    # (name, category, base_cost, base_sale_price)
    ("Wireless Mouse", "Electronics", 250, 450),
    ("USB-C Cable", "Electronics", 80, 180),
    ("Bluetooth Earphones", "Electronics", 600, 999),
    ("LED Desk Lamp", "Electronics", 350, 650),
    ("Power Bank 10000mAh", "Electronics", 500, 899),
    ("Basmati Rice 5kg", "Groceries", 400, 520),
    ("Sunflower Oil 1L", "Groceries", 120, 165),
    ("Toor Dal 1kg", "Groceries", 90, 130),
    ("Tea Powder 500g", "Groceries", 150, 210),
    ("Sugar 1kg", "Groceries", 40, 55,),
    ("Dish Soap 500ml", "Household", 60, 95,),
    ("Toilet Paper (Pack of 4)", "Household", 90, 140),
    ("Laundry Detergent 1kg", "Household", 140, 210),
    ("Hand Sanitizer 250ml", "Household", 70, 120),
    ("Air Freshener", "Household", 100, 160),
    ("Notebook (200 pages)", "Stationery", 30, 50),
    ("Ballpoint Pen (Pack of 10)", "Stationery", 40, 70),
    ("Stapler", "Stationery", 60, 110),
    ("Sticky Notes Pack", "Stationery", 35, 60),
    ("A4 Paper Ream", "Stationery", 220, 320),
]

random.seed(42)  # reproducible sample data

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            quantity INTEGER,
            price REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity_sold INTEGER,
            sale_price REAL,
            sale_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity_added INTEGER,
            purchase_price REAL,
            purchase_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def seed():
    conn = connect_db()
    cursor = conn.cursor()

    # Clear existing data for a clean seed (safe since this is sample/demo data)
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM purchases")
    cursor.execute("DELETE FROM products")
    conn.commit()

    product_ids = {}

    # ---- 2. Insert products with a starting stock level ----
    for name, category, cost, sale_price in PRODUCTS:
        starting_qty = random.randint(20, 100)
        cursor.execute(
            "INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
            (name, starting_qty, sale_price)
        )
        product_ids[name] = cursor.lastrowid
    conn.commit()

    # ---- 3. Generate purchase history (stock replenishment) over the last 180 days ----
    today = datetime.now()
    start_date = today - timedelta(days=180)

    for name, category, cost, sale_price in PRODUCTS:
        pid = product_ids[name]
        num_purchases = random.randint(3, 8)  # restocked 3-8 times over 6 months
        for _ in range(num_purchases):
            days_ago = random.randint(0, 180)
            purchase_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            qty = random.randint(20, 80)
            # small random cost variation to feel realistic
            price = round(cost * random.uniform(0.95, 1.08), 2)
            cursor.execute(
                "INSERT INTO purchases (product_id, quantity_added, purchase_price, purchase_date) VALUES (?, ?, ?, ?)",
                (pid, qty, price, purchase_date)
            )

    # ---- 4. Generate sales history — with deliberate variation so some products
    #          are clear "best sellers" and some are clear "slow movers" ----
    # Assign each product a popularity tier so the analysis has real signal
    popularity_tiers = {}
    for name, *_ in PRODUCTS:
        popularity_tiers[name] = random.choices(
            ["high", "medium", "low"], weights=[0.3, 0.4, 0.3]
        )[0]

    sale_count_by_tier = {"high": (25, 40), "medium": (10, 24), "low": (2, 9)}

    for name, category, cost, sale_price in PRODUCTS:
        pid = product_ids[name]
        tier = popularity_tiers[name]
        num_sales = random.randint(*sale_count_by_tier[tier])
        for _ in range(num_sales):
            days_ago = random.randint(0, 180)
            sale_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            qty = random.randint(1, 6)
            price = round(sale_price * random.uniform(0.97, 1.05), 2)
            cursor.execute(
                "INSERT INTO sales (product_id, quantity_sold, sale_price, sale_date) VALUES (?, ?, ?, ?)",
                (pid, qty, price, sale_date)
            )

    conn.commit()

    # ---- 5. Summary ----
    cursor.execute("SELECT COUNT(*) FROM products")
    n_products = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sales")
    n_sales = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM purchases")
    n_purchases = cursor.fetchone()[0]

    conn.close()

    print("Seed complete!")
    print(f"Products:  {n_products}")
    print(f"Sales:     {n_sales}")
    print(f"Purchases: {n_purchases}")


if __name__ == "__main__":
    seed()
