import os
from datetime import datetime

from connect import get_connection

EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
# Công thức doanh thu dùng chung cho app và Tableau
REVENUE_EXPR = "CAST(od.Quantity AS FLOAT) * od.UnitPrice * (1 - od.Discount / 100.0)"


def _fetch_all(sql, params=None):
    # Chạy query và đổi kết quả sang list dict
    conn = get_connection()
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)
    columns = [col[0] for col in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    conn.close()
    return rows


def get_kpi_summary():
    # Tính các chỉ số tổng quan trên giao diện
    sql = f"""
    SELECT
        COUNT(DISTINCT o.OrderID) AS total_orders,
        ISNULL(SUM({REVENUE_EXPR}), 0) AS total_revenue,
        COUNT(DISTINCT o.CustomerID) AS total_customers
    FROM Orders o
    INNER JOIN OrderDetails od ON o.OrderID = od.OrderID
    """
    rows = _fetch_all(sql)
    data = rows[0] if rows else {}

    top_sql = """
    SELECT TOP 1 p.ProductName AS top_product,
           SUM(od.Quantity) AS total_qty
    FROM OrderDetails od
    INNER JOIN Products p ON od.ProductID = p.ProductID
    GROUP BY p.ProductName
    ORDER BY SUM(od.Quantity) DESC
    """
    top = _fetch_all(top_sql)
    if top:
        data["top_product"] = top[0]["top_product"]
        data["top_product_qty"] = top[0]["total_qty"]
    else:
        data["top_product"] = "?"
        data["top_product_qty"] = 0
    return data


def get_top_products(limit=5):
    # Lấy top sản phẩm theo số lượng bán
    sql = f"""
    SELECT TOP ({int(limit)})
        p.ProductName AS product_name,
        SUM(od.Quantity) AS quantity,
        SUM({REVENUE_EXPR}) AS revenue
    FROM OrderDetails od
    INNER JOIN Products p ON od.ProductID = p.ProductID
    GROUP BY p.ProductName
    ORDER BY SUM(od.Quantity) DESC
    """
    return _fetch_all(sql)


def get_revenue_by_city():
    # Tính doanh thu theo thành phố
    sql = f"""
    SELECT c.City AS city,
           SUM({REVENUE_EXPR}) AS revenue
    FROM Orders o
    INNER JOIN Customers c ON o.CustomerID = c.CustomerID
    INNER JOIN OrderDetails od ON o.OrderID = od.OrderID
    GROUP BY c.City
    ORDER BY revenue DESC
    """
    return _fetch_all(sql)


def get_revenue_by_month():
    # Tính doanh thu theo tháng
    sql = f"""
    SELECT YEAR(o.OrderDate) AS order_year,
           MONTH(o.OrderDate) AS order_month,
           SUM({REVENUE_EXPR}) AS revenue
    FROM Orders o
    INNER JOIN OrderDetails od ON o.OrderID = od.OrderID
    GROUP BY YEAR(o.OrderDate), MONTH(o.OrderDate)
    ORDER BY order_year, order_month
    """
    return _fetch_all(sql)


def export_for_tableau():
    # Xuất dữ liệu đã xử lý ra CSV cho Tableau
    import pandas as pd
    from connect import connect_str

    os.makedirs(EXPORT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(EXPORT_DIR, f"sales_for_tableau_{timestamp}.csv")

    conn = connect_str()
    if conn is None:
        raise ConnectionError("Cannot connect to SQL Server for CSV export.")

    try:
        sql_fallback = """
        SELECT o.OrderID, o.OrderDate, c.FullName AS CustomerName, c.City,
               e.FullName AS EmployeeName, p.ProductName, cat.CategoryName,
               od.Quantity, od.UnitPrice, od.Discount,
               CAST(od.Quantity * od.UnitPrice * (1 - od.Discount / 100.0) AS DECIMAL(18,2)) AS Revenue,
               CAST(od.Quantity * (od.UnitPrice * (1 - od.Discount / 100.0) - p.Cost) AS DECIMAL(18,2)) AS Profit,
               pay.PaymentMethod, pay.PaymentAmount
        FROM Orders o
        INNER JOIN Customers c ON o.CustomerID = c.CustomerID
        INNER JOIN Employees e ON o.EmployeeID = e.EmployeeID
        INNER JOIN OrderDetails od ON o.OrderID = od.OrderID
        INNER JOIN Products p ON od.ProductID = p.ProductID
        INNER JOIN Categories cat ON p.CategoryID = cat.CategoryID
        LEFT JOIN Payments pay ON o.OrderID = pay.OrderID
        """
        try:
            # Ưu tiên view nếu database đã tạo sẵn
            df = pd.read_sql("SELECT * FROM vw_SalesForTableau", conn)
            required_columns = {"Discount", "UnitPrice", "Revenue", "Profit", "PaymentMethod", "PaymentAmount", "CategoryName"}
            if not required_columns.issubset(set(df.columns)):
                df = pd.read_sql(sql_fallback, conn)
        except Exception:
            # Nếu view lỗi thì dùng query join trực tiếp
            df = pd.read_sql(sql_fallback, conn)

        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        return filepath
    finally:
        conn.close()

