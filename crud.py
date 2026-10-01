# -*- coding: utf-8 -*-
from connect import get_connection

DEFAULT_DISCOUNT = 0
DEFAULT_PAYMENT_METHOD = "Cash"

# Helper dùng chung cho CRUD đơn hàng
# Lấy danh sách đơn hàng để hiển thị
_SQL_SELECT_ORDERS = """
SELECT
    o.OrderID,
    c.FullName AS CustomerName,
    e.FullName AS EmployeeName,
    p.ProductName,
    od.Quantity,
    od.UnitPrice AS Price,
    od.Discount,
    ISNULL(pay.PaymentMethod, 'Cash') AS PaymentMethod,
    ISNULL(pay.PaymentAmount, 0) AS PaymentAmount,
    o.OrderDate,
    od.OrderDetailID,
    o.CustomerID,
    o.EmployeeID,
    od.ProductID
FROM Orders o
INNER JOIN Customers c ON o.CustomerID = c.CustomerID
INNER JOIN Employees e ON o.EmployeeID = e.EmployeeID
INNER JOIN OrderDetails od ON o.OrderID = od.OrderID
INNER JOIN Products p ON od.ProductID = p.ProductID
LEFT JOIN Payments pay ON o.OrderID = pay.OrderID
"""




def _get_product_price(cursor, product_id):
    # Lấy đơn giá hiện tại của sản phẩm
    """Get the current product price from Products."""
    cursor.execute("SELECT Price FROM Products WHERE ProductID = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"ProductID={product_id} was not found.")
    return float(row.Price)


def _calculate_total_amount(quantity, unit_price, discount=DEFAULT_DISCOUNT):
    # Tính doanh thu theo số lượng, đơn giá và giảm giá
    return float(quantity) * float(unit_price) * (1 - float(discount) / 100)


def _recalculate_order_total(cursor, order_id):
    # Tính lại tổng tiền khi đơn hàng còn nhiều dòng chi tiết
    """Recalculate TotalAmount from remaining OrderDetails rows."""
    cursor.execute(
        """
        SELECT ISNULL(
            SUM(CAST(Quantity AS FLOAT) * UnitPrice * (1 - Discount / 100.0)),
            0
        )
        FROM OrderDetails
        WHERE OrderID = ?
        """,
        (order_id,),
    )
    total_amount = float(cursor.fetchone()[0] or 0)
    cursor.execute(
        "UPDATE Orders SET TotalAmount = ? WHERE OrderID = ?",
        (total_amount, order_id),
    )
    cursor.execute(
        "UPDATE Payments SET PaymentAmount = ? WHERE OrderID = ?",
        (total_amount, order_id),
    )
    return total_amount


def _row_to_dict(row):
    # Đổi row SQL Server sang dict để UI dễ đọc
    return {
        "order_id": row.OrderID,
        "customer_name": row.CustomerName,
        "employee_name": row.EmployeeName,
        "product_name": row.ProductName,
        "quantity": row.Quantity,
        "price": float(row.Price),
        "discount": float(row.Discount or 0),
        "payment_method": row.PaymentMethod,
        "payment_amount": float(row.PaymentAmount),
        "order_date": row.OrderDate,
        "order_detail_id": row.OrderDetailID,
        "customer_id": row.CustomerID,
        "employee_id": row.EmployeeID,
        "product_id": row.ProductID,
    }




def get_customers():
    # Lấy danh sách khách hàng
    """Read Customers for the form combobox."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT CustomerID, FullName FROM Customers ORDER BY FullName"
    )
    result = [(row.CustomerID, row.FullName) for row in cursor.fetchall()]
    conn.close()
    return result


def get_all_customers_detail():
    # Lấy đầy đủ thông tin khách hàng cho popup
    """Get full customer details for Manage Customers."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT CustomerID, FullName, Gender, Age, City, Country, Email, CreatedDate
            FROM Customers
            ORDER BY CustomerID DESC
            """
        )
        return [
            {
                "customer_id": row.CustomerID,
                "full_name": row.FullName,
                "gender": row.Gender,
                "age": row.Age,
                "city": row.City,
                "country": row.Country,
                "email": row.Email,
                "created_date": row.CreatedDate,
            }
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()


def insert_customer(full_name, gender, age, city, country, email):
    # Thêm khách hàng mới
    """Insert a customer and return the new CustomerID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            INSERT INTO Customers (FullName, Gender, Age, City, Country, Email)
            OUTPUT INSERTED.CustomerID
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (full_name, gender, age, city, country, email),
        )
        customer_id = cursor.fetchone()[0]
        conn.commit()
        return customer_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_customer(customer_id, full_name, gender, age, city, country, email):
    # Cập nhật thông tin khách hàng
    """Update a customer by CustomerID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            UPDATE Customers
            SET FullName = ?, Gender = ?, Age = ?, City = ?, Country = ?, Email = ?
            WHERE CustomerID = ?
            """,
            (full_name, gender, age, city, country, email, customer_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_customer(customer_id):
    # Không cho xóa khách hàng nếu đã có đơn hàng
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra khóa ngoại trước khi xóa
        cursor.execute(
            "SELECT COUNT(*) FROM Orders WHERE CustomerID = ?",
            (customer_id,),
        )
        order_count = cursor.fetchone()[0]
        if order_count > 0:
            raise Exception("Cannot delete this customer because related orders exist.")

        cursor.execute("DELETE FROM Customers WHERE CustomerID = ?", (customer_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_employees():
    # Lấy danh sách nhân viên
    """Read Employees for the combobox."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT EmployeeID, FullName FROM Employees ORDER BY FullName"
    )
    result = [(row.EmployeeID, row.FullName) for row in cursor.fetchall()]
    conn.close()
    return result


def get_all_employees_detail():
    # Lấy đầy đủ thông tin nhân viên cho popup
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT EmployeeID, FullName, Department, PositionName, HireDate
            FROM Employees
            ORDER BY EmployeeID DESC
            """
        )
        return [
            {
                "employee_id": row.EmployeeID,
                "full_name": row.FullName,
                "department": row.Department,
                "position_name": row.PositionName,
                "hire_date": row.HireDate,
            }
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()


def insert_employee(full_name, department, position_name, hire_date):
    # Thêm nhân viên mới
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            INSERT INTO Employees (FullName, Department, PositionName, HireDate)
            OUTPUT INSERTED.EmployeeID
            VALUES (?, ?, ?, ?)
            """,
            (full_name, department, position_name, hire_date),
        )
        employee_id = cursor.fetchone()[0]
        conn.commit()
        return employee_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_employee(employee_id, full_name, department, position_name, hire_date):
    # Cập nhật thông tin nhân viên
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            UPDATE Employees
            SET FullName = ?, Department = ?, PositionName = ?, HireDate = ?
            WHERE EmployeeID = ?
            """,
            (full_name, department, position_name, hire_date, employee_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_employee(employee_id):
    # Không cho xóa nhân viên nếu đã có đơn hàng
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra đơn hàng liên quan trước khi xóa
        cursor.execute("SELECT COUNT(*) FROM Orders WHERE EmployeeID = ?", (employee_id,))
        order_count = cursor.fetchone()[0]
        if order_count > 0:
            raise Exception("Cannot delete this employee because related orders exist.")
        cursor.execute("DELETE FROM Employees WHERE EmployeeID = ?", (employee_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_products():
    # Lấy danh sách sản phẩm
    """Read Products with price for the combobox."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT ProductID, ProductName, Price
        FROM Products
        ORDER BY ProductName
        """
    )
    result = [
        (row.ProductID, row.ProductName, float(row.Price))
        for row in cursor.fetchall()
    ]
    conn.close()
    return result

def get_categories():
    # Lấy danh sách danh mục
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryName")
        return [(row.CategoryID, row.CategoryName) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_categories_detail():
    # Lấy đầy đủ danh mục cho popup
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID DESC")
        return [
            {"category_id": row.CategoryID, "category_name": row.CategoryName}
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()


def insert_category(category_name):
    # Thêm danh mục mới
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            INSERT INTO Categories (CategoryName)
            OUTPUT INSERTED.CategoryID
            VALUES (?)
            """,
            (category_name,),
        )
        category_id = cursor.fetchone()[0]
        conn.commit()
        return category_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_category(category_id, category_name):
    # Cập nhật tên danh mục
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?",
            (category_name, category_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_category(category_id):
    # Không cho xóa danh mục nếu đang có sản phẩm
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra sản phẩm liên quan trước khi xóa
        cursor.execute("SELECT COUNT(*) FROM Products WHERE CategoryID = ?", (category_id,))
        product_count = cursor.fetchone()[0]
        if product_count > 0:
            raise Exception("Cannot delete this category because related products exist.")
        cursor.execute("DELETE FROM Categories WHERE CategoryID = ?", (category_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_all_products_detail():
    # Lấy đầy đủ thông tin sản phẩm cho popup
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT p.ProductID, p.ProductName, p.CategoryID, c.CategoryName, p.Price, p.Cost
            FROM Products p
            INNER JOIN Categories c ON p.CategoryID = c.CategoryID
            ORDER BY p.ProductID DESC
            """
        )
        return [
            {
                "product_id": row.ProductID,
                "product_name": row.ProductName,
                "category_id": row.CategoryID,
                "category_name": row.CategoryName,
                "price": float(row.Price),
                "cost": float(row.Cost),
            }
            for row in cursor.fetchall()
        ]
    finally:
        conn.close()


def insert_product(product_name, category_id, price, cost):
    # Thêm sản phẩm mới
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            INSERT INTO Products (ProductName, CategoryID, Price, Cost)
            OUTPUT INSERTED.ProductID
            VALUES (?, ?, ?, ?)
            """,
            (product_name, category_id, price, cost),
        )
        product_id = cursor.fetchone()[0]
        conn.commit()
        return product_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_product(product_id, product_name, category_id, price, cost):
    # Cập nhật thông tin sản phẩm
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            UPDATE Products
            SET ProductName = ?, CategoryID = ?, Price = ?, Cost = ?
            WHERE ProductID = ?
            """,
            (product_name, category_id, price, cost, product_id),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_product(product_id):
    # Không cho xóa sản phẩm nếu đã phát sinh đơn hàng
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra chi tiết đơn hàng trước khi xóa
        cursor.execute("SELECT COUNT(*) FROM OrderDetails WHERE ProductID = ?", (product_id,))
        detail_count = cursor.fetchone()[0]
        if detail_count > 0:
            raise Exception("Cannot delete this product because related orders exist.")

        cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



def get_all_orders():
    # Lấy danh sách đơn hàng để hiển thị
    conn = get_connection()
    cursor = conn.cursor()
    sql = _SQL_SELECT_ORDERS + " ORDER BY o.OrderID DESC, od.OrderDetailID"
    cursor.execute(sql)
    data = [_row_to_dict(row) for row in cursor.fetchall()]  # List dict
    conn.close()
    return data


def search_orders(search_type, keyword):
    # Tìm kiếm đơn hàng theo điều kiện cơ bản
    """
    Search by order_id / customer / product.
    search_type: 'order_id' | 'customer' | 'product'
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return get_all_orders()

    conn = get_connection()
    cursor = conn.cursor()
    sql = _SQL_SELECT_ORDERS + " WHERE 1=1"
    params = []

    if search_type == "order_id":
        sql += " AND CAST(o.OrderID AS NVARCHAR(20)) LIKE ?"
        params.append(f"%{keyword}%")
    elif search_type == "customer":
        sql += " AND c.FullName LIKE ?"
        params.append(f"%{keyword}%")
    elif search_type == "product":
        sql += " AND p.ProductName LIKE ?"
        params.append(f"%{keyword}%")

    sql += " ORDER BY o.OrderID DESC, od.OrderDetailID"
    cursor.execute(sql, params)
    data = [_row_to_dict(row) for row in cursor.fetchall()]
    conn.close()
    return data


def insert_order(
    customer_id,
    employee_id,
    product_id,
    quantity,
    order_date,
    payment_method=DEFAULT_PAYMENT_METHOD,
    discount=DEFAULT_DISCOUNT,
    payment_amount=None,
):
    # Thêm đơn hàng mới vào Orders, OrderDetails và Payments
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Lấy giá hiện tại rồi tính tổng tiền
        unit_price = _get_product_price(cursor, product_id)
        discount = DEFAULT_DISCOUNT if discount in (None, "") else float(discount)
        total_amount = _calculate_total_amount(quantity, unit_price, discount)
        payment_amount = total_amount if payment_amount is None else float(payment_amount)

        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, TotalAmount)
            OUTPUT INSERTED.OrderID
            VALUES (?, ?, ?, ?)
            """,
            (customer_id, employee_id, order_date, total_amount),
        )
        order_id = cursor.fetchone()[0]

        cursor.execute(
            """
            INSERT INTO OrderDetails
                (OrderID, ProductID, Quantity, UnitPrice, Discount)
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, product_id, quantity, unit_price, discount),
        )

        cursor.execute(
            """
            INSERT INTO Payments
                (OrderID, PaymentMethod, PaymentDate, PaymentAmount)
            VALUES (?, ?, ?, ?)
            """,
            (order_id, payment_method, order_date, payment_amount),
        )

        conn.commit()
        return order_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()




def update_order(
    order_id,
    order_detail_id,
    customer_id,
    employee_id,
    product_id,
    quantity,
    order_date,
    payment_method=DEFAULT_PAYMENT_METHOD,
    discount=DEFAULT_DISCOUNT,
    payment_amount=None,
):
    # Cập nhật đơn hàng và tính lại tổng tiền
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Tính lại tổng tiền sau khi đổi sản phẩm, số lượng hoặc giảm giá
        unit_price = _get_product_price(cursor, product_id)
        discount = DEFAULT_DISCOUNT if discount in (None, "") else float(discount)
        total_amount = _calculate_total_amount(quantity, unit_price, discount)
        payment_amount = total_amount if payment_amount is None else float(payment_amount)

        # Dùng transaction để rollback nếu có lỗi
        cursor.execute(
            """
            UPDATE Orders
            SET CustomerID = ?, EmployeeID = ?, OrderDate = ?, TotalAmount = ?
            WHERE OrderID = ?
            """,
            (customer_id, employee_id, order_date, total_amount, order_id),
        )

        cursor.execute(
            """
            UPDATE OrderDetails
            SET ProductID = ?, Quantity = ?, UnitPrice = ?, Discount = ?
            WHERE OrderDetailID = ?
            """,
            (product_id, quantity, unit_price, discount, order_detail_id),
        )

        cursor.execute("SELECT PaymentID FROM Payments WHERE OrderID = ?", (order_id,))
        payment_row = cursor.fetchone()
        if payment_row:
            cursor.execute(
                """
                UPDATE Payments
                SET PaymentMethod = ?, PaymentDate = ?, PaymentAmount = ?
                WHERE OrderID = ?
                """,
                (payment_method, order_date, payment_amount, order_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO Payments
                    (OrderID, PaymentMethod, PaymentDate, PaymentAmount)
                VALUES (?, ?, ?, ?)
                """,
                (order_id, payment_method, order_date, payment_amount),
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()




def delete_order(order_id, order_detail_id):
    # Xóa đơn hàng, xóa dữ liệu liên quan trước
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Xóa bảng con trước để tránh lỗi khóa ngoại
        cursor.execute(
            "DELETE FROM OrderDetails WHERE OrderDetailID = ?",
            (order_detail_id,),
        )

        cursor.execute(
            "SELECT COUNT(*) FROM OrderDetails WHERE OrderID = ?",
            (order_id,),
        )
        count_remaining = cursor.fetchone()[0]

        if count_remaining == 0:
            # Không còn dòng chi tiết thì xóa luôn payment và order
            cursor.execute("DELETE FROM Payments WHERE OrderID = ?", (order_id,))
            cursor.execute("DELETE FROM Orders WHERE OrderID = ?", (order_id,))
        else:
            _recalculate_order_total(cursor, order_id)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_distinct_customer_cities():
    # Lấy danh sách thành phố để lọc đơn hàng
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT DISTINCT City
            FROM Customers
            WHERE City IS NOT NULL AND LTRIM(RTRIM(City)) <> ''
            ORDER BY City
            """
        )
        return [row.City for row in cursor.fetchall()]
    finally:
        conn.close()


def search_orders_advanced(
    keyword=None,
    search_by=None,
    from_date=None,
    to_date=None,
    city=None,
    category_id=None,
):
    # Lọc đơn hàng theo ngày, thành phố và danh mục
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = _SQL_SELECT_ORDERS + " WHERE 1=1"
        params = []
        keyword = (keyword or "").strip()
        search_by = search_by or ""

        if keyword:
            if search_by == "order_id":
                sql += " AND o.OrderID = ?"
                params.append(int(keyword))
            elif search_by == "customer":
                sql += " AND c.FullName LIKE ?"
                params.append(f"%{keyword}%")
            elif search_by == "product":
                sql += " AND p.ProductName LIKE ?"
                params.append(f"%{keyword}%")

        if from_date:
            sql += " AND o.OrderDate >= ?"
            params.append(from_date)
        if to_date:
            sql += " AND o.OrderDate <= ?"
            params.append(to_date)
        if city:
            sql += " AND c.City = ?"
            params.append(city)
        if category_id:
            sql += " AND p.CategoryID = ?"
            params.append(category_id)

        sql += " ORDER BY o.OrderID DESC, od.OrderDetailID"
        cursor.execute(sql, params)
        return [_row_to_dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

