import sqlite3

def connect_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    # PRODUCTS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            quantity INTEGER,
            price REAL
        )
    """)

    # SALES TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity_sold INTEGER,
            sale_price REAL,
            sale_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # PURCHASES TABLE
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


def add_product(name, quantity, price):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
            (name, quantity, price)
        )
        conn.commit()
        print("✅ Product added successfully!")
    except sqlite3.IntegrityError:
        print("❌ Product already exists! Try updating instead.")
    finally:
        conn.close()


def view_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    return data


def search_product(keyword):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{keyword}%",))
    data = cursor.fetchall()
    conn.close()
    return data


def update_quantity(product_id, new_quantity):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
    conn.commit()
    conn.close()


def get_product_by_id(product_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    data = cursor.fetchone()
    conn.close()
    return data


def stock_in(product_id, amount):
    product = get_product_by_id(product_id)

    if not product:
        print("❌ Product not found!")
        return

    new_qty = product[2] + amount
    update_quantity(product_id, new_qty)
    print("✅ Stock added successfully!")


def stock_out(product_id, amount):
    product = get_product_by_id(product_id)

    if not product:
        print("❌ Product not found!")
        return

    if product[2] < amount:
        print("❌ Not enough stock available!")
        return

    new_qty = product[2] - amount
    update_quantity(product_id, new_qty)
    print("✅ Stock removed successfully!")


def low_stock(threshold=5):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE quantity < ?", (threshold,))
    data = cursor.fetchall()
    conn.close()
    return data


def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def record_sale(product_id, qty, sale_price):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (product_id, quantity_sold, sale_price) VALUES (?, ?, ?)",
        (product_id, qty, sale_price)
    )
    conn.commit()
    conn.close()


def record_purchase(product_id, qty, purchase_price):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO purchases (product_id, quantity_added, purchase_price) VALUES (?, ?, ?)",
        (product_id, qty, purchase_price)
    )
    conn.commit()
    conn.close()


def view_sales():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sales.sale_id, products.name, sales.quantity_sold, sales.sale_price, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
    """)
    data = cursor.fetchall()
    conn.close()
    return data


def view_purchases():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT purchases.purchase_id, products.name, purchases.quantity_added, purchases.purchase_price, purchases.purchase_date
        FROM purchases
        JOIN products ON purchases.product_id = products.id
    """)
    data = cursor.fetchall()
    conn.close()
    return data
