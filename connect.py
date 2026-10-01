# -*- coding: utf-8 -*-
import pyodbc

# Cấu hình kết nối SQL Server
SERVER = "localhost"
DATABASE = "TableauAnalysisDB"
DRIVER = "ODBC Driver 17 for SQL Server"


def connect_str():
    # Tạo kết nối tới SQL Server
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception:
        # Không raise ở đây để UI tự hiện lỗi dễ nhìn hơn
        return None


def get_connection():
    # Trả về connection hoặc báo lỗi nếu không kết nối được
    conn = connect_str()
    if conn is None:
        raise ConnectionError(
            f"Cannot connect to SQL Server.\nSERVER={SERVER}\nDATABASE={DATABASE}"
        )
    return conn


def test_connection():
    # Kiểm tra nhanh kết nối database
    try:
        conn = connect_str()
        if conn is None:
            return False, (
                f"Cannot connect.\nSERVER={SERVER}\nDATABASE={DATABASE}\n"
                "Run the .sql file in SSMS first or check the ODBC driver."
            )

        cursor = conn.cursor()
        # Lấy tên database hiện tại để kiểm tra có vào đúng DB không
        cursor.execute("SELECT DB_NAME() AS DbName")
        row = cursor.fetchone()
        db_name = row[0] if row else "?"
        conn.close()

        return True, f"Connection successful.\nCurrent database: {db_name}"
    except Exception as error:
        return False, str(error)
