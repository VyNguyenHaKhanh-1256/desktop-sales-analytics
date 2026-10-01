# -*- coding: utf-8 -*-
import glob
import os
import subprocess
import webbrowser

import analytics


def get_guide_text():
    # Trả về hướng dẫn kết nối Tableau
    return (
        "Tableau SQL Server Connection Guide\n\n"
        "1. Open Tableau Desktop.\n"
        "2. Select Microsoft SQL Server in Connect.\n"
        "3. Enter Server: localhost.\n"
        "4. Select Database: TableauAnalysisDB.\n"
        "5. Use Live connection.\n"
        "6. Use vw_SalesForTableau if available, or manually connect Orders, "
        "OrderDetails, Products, Categories, Customers, Employees and Payments.\n"
        "7. Build worksheets using OrderDate, City, ProductName, CategoryName, "
        "Quantity, UnitPrice, Discount, Revenue, PaymentMethod and PaymentAmount.\n"
        "8. After CRUD operations in the Python app, refresh Tableau using Data -> Refresh.\n"
    )


def find_tableau_executable():
    # Tìm file chạy Tableau trong Program Files
    patterns = [
        r"C:\Program Files\Tableau\Tableau *\bin\tableau.exe",
        r"C:\Program Files (x86)\Tableau\Tableau *\bin\tableau.exe",
    ]

    for pattern in patterns:
        matches = sorted(glob.glob(pattern), reverse=True)
        if matches:
            return matches[0]

    return None


def open_tableau_desktop():
    # Mở Tableau Desktop nếu máy đã cài
    exe = find_tableau_executable()

    if not exe:
        return False, (
            "Tableau Desktop was not found on this computer.\n"
            "Open Tableau manually and connect to SQL Server:\n"
            "Server: localhost\n"
            "Database: TableauAnalysisDB"
        )

    try:
        subprocess.Popen([exe], shell=False)
        return True, f"Tableau Desktop opened:\n{exe}"
    except Exception as e:
        return False, f"Cannot open Tableau Desktop:\n{e}"


def open_exports_folder():
    # Mở thư mục chứa file export
    os.makedirs(analytics.EXPORT_DIR, exist_ok=True)
    os.startfile(analytics.EXPORT_DIR)
    return analytics.EXPORT_DIR


def open_tableau_help_online():
    # Mở trang hướng dẫn Tableau trên trình duyệt
    webbrowser.open(
        "https://help.tableau.com/current/pro/desktop/en-us/examples_sqlserver.htm"
    )
