"""
export_analysis.py
Exports the inventory/sales analysis results to CSV files inside a
`dashboard/` folder, ready to be imported into Power BI.

Usage:
    python export_analysis.py
"""

import os
import sqlite3
import pandas as pd
from sales_analysis import (
    get_connection,
    best_selling_products,
    slow_moving_products,
    profit_margin_by_product,
    revenue_by_category,
    stock_turnover_rate,
)

OUTPUT_DIR = "dashboard"


def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = get_connection()

    # 1. Best sellers (top 20, not just top 5, for a fuller dashboard view)
    best_sellers = best_selling_products(conn, top_n=20)
    best_sellers.to_csv(f"{OUTPUT_DIR}/best_selling_products.csv", index=False)

    # 2. Slow movers (all 20 products, sorted slowest first)
    slow_movers = slow_moving_products(conn, top_n=20)
    slow_movers.to_csv(f"{OUTPUT_DIR}/slow_moving_products.csv", index=False)

    # 3. Profit margin by product
    margins = profit_margin_by_product(conn)
    margins.to_csv(f"{OUTPUT_DIR}/profit_margin_by_product.csv", index=False)

    # 4. Revenue by category
    revenue = revenue_by_category(conn).reset_index()
    revenue.columns = ["category", "revenue"]
    revenue.to_csv(f"{OUTPUT_DIR}/revenue_by_category.csv", index=False)

    # 5. Stock turnover (all products)
    turnover = stock_turnover_rate(conn)
    turnover.to_csv(f"{OUTPUT_DIR}/stock_turnover.csv", index=False)

    # 6. A combined master file — one row per product with everything joined
    #    together, which is the easiest single file to build a Power BI
    #    dashboard from (fewer files to relate/join inside Power BI itself)
    master_query = """
        SELECT
            p.id,
            p.name,
            p.quantity AS current_stock,
            p.price AS list_price,
            COALESCE(SUM(DISTINCT s.quantity_sold), 0) AS placeholder
        FROM products p
        LEFT JOIN sales s ON s.product_id = p.id
        GROUP BY p.id
    """
    # Build the master table by merging our already-computed frames instead
    # (cleaner than a single mega-query with duplicate joins)
    master = margins.merge(
        best_sellers[["name", "total_units_sold", "total_revenue"]],
        on="name", how="left"
    )
    master = master.merge(
        turnover[["name", "current_stock", "turnover_rate"]],
        on="name", how="left"
    )
    master["total_units_sold"] = master["total_units_sold"].fillna(0)
    master["total_revenue"] = master["total_revenue"].fillna(0)

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
    master["category"] = master["name"].map(category_map)
    master.to_csv(f"{OUTPUT_DIR}/inventory_master.csv", index=False)

    conn.close()

    print("Export complete! Files saved to /dashboard:")
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".csv"):
            print(" -", f)


if __name__ == "__main__":
    export_all()
