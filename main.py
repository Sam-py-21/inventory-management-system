from database import (
    add_product, view_products, delete_product,
    stock_in, stock_out, search_product, low_stock,
    record_sale, record_purchase, view_sales, view_purchases
)
from inventory_analysis import inventory_value, average_stock, max_stock_product
from export_excel import export_to_excel
from utils import get_int, get_float, get_non_empty_string


def print_products(products):
    if not products:
        print("❌ No products found.")
        return

    print("\nID   Name              Qty   Price")
    print("--------------------------------------")
    for p in products:
        print(f"{p[0]:<4} {p[1]:<17} {p[2]:<5} {p[3]}")

def print_sales(data):
    if not data:
        print("❌ No sales found.")
        return

    print("\nSaleID  Product           Qty   Price   Date")
    print("---------------------------------------------------------")
    for row in data:
        print(f"{row[0]:<7} {row[1]:<16} {row[2]:<5} {row[3]:<7} {row[4]}")


def print_purchases(data):
    if not data:
        print("❌ No purchases found.")
        return

    print("\nPurchaseID  Product           Qty   Price   Date")
    print("---------------------------------------------------------")
    for row in data:
        print(f"{row[0]:<10} {row[1]:<16} {row[2]:<5} {row[3]:<7} {row[4]}")


def menu():
    while True:
        print("\n========= Inventory Management =========")
        print("1. Add Product")
        print("2. View Products")
        print("3. Search Product")
        print("4. Stock In")
        print("5. Stock Out")
        print("6. Low Stock Alert")
        print("7. Analytics (NumPy)")
        print("8. Export to Excel")
        print("9. Delete Product")
        print("10. Sell Product")
        print("11. Purchase Stock")
        print("12. View Sales Report")
        print("13. View Purchase Report")
        print("0. Exit")

        choice = input("Enter option: ").strip()

        if choice == "1":
            name = get_non_empty_string("Product Name: ")
            qty = get_int("Quantity: ")
            price = get_float("Price: ")

            if qty < 0:
                print("❌ Quantity cannot be negative!")
                continue
            if price <= 0:
                print("❌ Price must be greater than 0!")
                continue

            add_product(name, qty, price)

        elif choice == "2":
            print_products(view_products())

        elif choice == "3":
            keyword = get_non_empty_string("Enter product name keyword: ")
            print_products(search_product(keyword))

        elif choice == "4":
            pid = get_int("Enter Product ID: ")
            amount = get_int("Enter Stock In amount: ")

            if amount <= 0:
                print("❌ Amount must be greater than 0!")
                continue

            stock_in(pid, amount)

        elif choice == "5":
            pid = get_int("Enter Product ID: ")
            amount = get_int("Enter Stock Out amount: ")

            if amount <= 0:
                print("❌ Amount must be greater than 0!")
                continue

            stock_out(pid, amount)

        elif choice == "6":
            threshold = get_int("Enter low stock threshold (default 5): ")
            if threshold <= 0:
                threshold = 5
            print_products(low_stock(threshold))

        elif choice == "7":
            print("\n--- Analytics ---")
            print("Total Inventory Value:", inventory_value())
            print("Average Stock:", average_stock())
            print("Highest Stock Product:", max_stock_product())

        elif choice == "8":
            export_to_excel()

        elif choice == "9":
            pid = get_int("Enter Product ID to delete: ")
            delete_product(pid)
            print("✅ Product deleted.")

        elif choice == "10":
            pid = get_int("Enter Product ID: ")
            qty = get_int("Enter quantity to sell: ")
            sale_price = get_float("Enter selling price (per unit): ")

            if qty <= 0:
                print("❌ Quantity must be greater than 0!")
                continue

            stock_out(pid, qty)  # reduce stock
            record_sale(pid, qty, sale_price)  # save sale
            print("✅ Sale recorded successfully!")

        elif choice == "11":
            pid = get_int("Enter Product ID: ")
            qty = get_int("Enter quantity to purchase: ")
            purchase_price = get_float("Enter purchase price (per unit): ")

            if qty <= 0:
                print("❌ Quantity must be greater than 0!")
                continue

            stock_in(pid, qty)  # add stock
            record_purchase(pid, qty, purchase_price)  # save purchase
            print("✅ Purchase recorded successfully!")

        elif choice == "12":
            print_sales(view_sales())

        elif choice == "13":
            print_purchases(view_purchases())

        elif choice == "0":
            print("👋 Exiting program...")
            break

        else:
            print("❌ Invalid option!")
menu()
