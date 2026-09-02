"""
sales_analysis.py
SQL-based analysis on top of the Inventory Management System's database.
Calculates business-relevant metrics: best/slow sellers, profit margins,
revenue by category, and stock turnover.

Usage:
    python sales_analysis.py
"""

import sqlite3
import pandas as pd

DB_NAME = "inventory.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def best_selling_products(conn, top_n=5):
    """Products with the highest total quantity sold."""
    query = """
        SELECT
            p.name,
            SUM(s.quantity_sold) AS total_units_sold,
            SUM(s.quantity_sold * s.sale_price) AS total_revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_units_sold DESC
        LIMIT ?
    """
    return pd.read_sql(query, conn, params=(top_n,))


def slow_moving_products(conn, top_n=5):
    """Products with the lowest total quantity sold (dead stock risk)."""
    query = """
        SELECT
            p.name,
            p.quantity AS current_stock,
            COALESCE(SUM(s.quantity_sold), 0) AS total_units_sold
        FROM products p
        LEFT JOIN sales s ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_units_sold ASC
        LIMIT ?
    """
    return pd.read_sql(query, conn, params=(top_n,))


def profit_margin_by_product(conn):
    """
    Average profit margin per product: average sale price vs average purchase
    (cost) price. Margin % = (sale - cost) / sale * 100
    """
    query = """
        SELECT
            p.name,
            ROUND(AVG(s.sale_price), 2) AS avg_sale_price,
            ROUND(AVG(pu.purchase_price), 2) AS avg_cost_price
        FROM products p
        JOIN sales s ON s.product_id = p.id
        JOIN purchases pu ON pu.product_id = p.id
        GROUP BY p.name
    """
    df = pd.read_sql(query, conn)
    df["profit_margin_pct"] = round(
        (df["avg_sale_price"] - df["avg_cost_price"]) / df["avg_sale_price"] * 100, 1
    )
    return df.sort_values("profit_margin_pct", ascending=False)


def revenue_by_category(conn):
    """
    Revenue grouped by product category. Category isn't stored in the DB
    (only in the seed script), so this maps product names to categories
    the same way seed_data.py defined them.
    """
    category_map = {
        "Wireless Mouse": "Electronics", "USB-C Cable": "Electronics",
        "Bluetooth Earphones": "Electronics", "LED Desk Lamp": "Electronics",
        "Power Bank 10000mAh": "Electronics",
        "Basmati Rice 5kg": "Groceries", "Sunflower Oil 1L": "Groceries",
        "Toor Dal 1kg": "Groceries", "Tea Powder 500g": "Groceries",
        "Sugar 1kg": "Groceries",
        "Dish Soap 500ml": "Household", "Toilet Paper (Pack of 4)": "Household",
        "Laundry Detergent 1kg": "Household", "Hand Sanitizer 250ml": "Household",
        "Air Freshener": "Household",
        "Notebook (200 pages)": "Stationery", "Ballpoint Pen (Pack of 10)": "Stationery",
        "Stapler": "Stationery", "Sticky Notes Pack": "Stationery",
        "A4 Paper Ream": "Stationery",
    }

    query = """
        SELECT p.name, SUM(s.quantity_sold * s.sale_price) AS revenue
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
    """
    df = pd.read_sql(query, conn)
    df["category"] = df["name"].map(category_map)
    return df.groupby("category")["revenue"].sum().round(2).sort_values(ascending=False)


def stock_turnover_rate(conn):
    """
    Turnover rate = total units sold / average stock on hand.
    Higher = inventory moves faster (efficient). Lower = overstocked / slow.
    """
    query = """
        SELECT
            p.name,
            p.quantity AS current_stock,
            COALESCE(SUM(s.quantity_sold), 0) AS total_units_sold
        FROM products p
        LEFT JOIN sales s ON s.product_id = p.id
        GROUP BY p.name
    """
    df = pd.read_sql(query, conn)
    # avoid divide-by-zero for products with 0 current stock
    df["turnover_rate"] = df.apply(
        lambda row: round(row["total_units_sold"] / row["current_stock"], 2)
        if row["current_stock"] > 0 else None,
        axis=1
    )
    return df.sort_values("turnover_rate", ascending=False)


def run_full_analysis():
    conn = get_connection()

    print("\n=== TOP 5 BEST-SELLING PRODUCTS ===")
    print(best_selling_products(conn).to_string(index=False))

    print("\n=== TOP 5 SLOW-MOVING PRODUCTS ===")
    print(slow_moving_products(conn).to_string(index=False))

    print("\n=== PROFIT MARGIN BY PRODUCT ===")
    print(profit_margin_by_product(conn).to_string(index=False))

    print("\n=== REVENUE BY CATEGORY ===")
    print(revenue_by_category(conn).to_string())

    print("\n=== STOCK TURNOVER RATE (top 10) ===")
    print(stock_turnover_rate(conn).head(10).to_string(index=False))

    conn.close()


if __name__ == "__main__":
    run_full_analysis()
