import numpy as np
from database import view_products


def inventory_value():
    products = view_products()
    if not products:
        return 0

    prices = np.array([p[3] for p in products])
    qty = np.array([p[2] for p in products])
    total = np.sum(prices * qty)
    return total


def average_stock():
    products = view_products()
    if not products:
        return 0

    qty = np.array([p[2] for p in products])
    return round(np.mean(qty), 2)



def max_stock_product():
    products = view_products()
    if not products:
        return None

    p = max(products, key=lambda x: x[2])
    return f"{p[1]} (Qty: {p[2]})"

def total_products():
    products = view_products()
    return len(products)
