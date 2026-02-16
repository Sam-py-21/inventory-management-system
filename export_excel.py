import openpyxl
from database import view_products


def export_to_excel():
    data = view_products()

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Inventory Data"

    sheet.append(["ID", "Product Name", "Quantity", "Price"])

    for row in data:
        sheet.append(row)

    wb.save("inventory_data.xlsx")
    print("✅ Excel file created: inventory_data.xlsx")
