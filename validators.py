# -*- coding: utf-8 -*-
from datetime import datetime


# Các hàm kiểm tra dữ liệu nhập
def parse_int(value, field_name, min_value=None, max_value=None):
    # Chuyển chuỗi sang số nguyên
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return None, f"{field_name} must be an integer."
    if min_value is not None and number < min_value:
        return None, f"{field_name} must be >= {min_value}."
    if max_value is not None and number > max_value:
        return None, f"{field_name} must be <= {max_value}."
    return number, None


def parse_float(value, field_name, min_value=None, max_value=None):
    # Chuyển chuỗi sang số thực
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None, f"{field_name} must be a number."
    if min_value is not None and number < min_value:
        return None, f"{field_name} must be >= {min_value}."
    if max_value is not None and number > max_value:
        return None, f"{field_name} must be <= {max_value}."
    return number, None


def parse_money(value, field_name):
    # Chuyển chuỗi tiền tệ về dạng số
    return parse_float(str(value).replace(",", ""), field_name, min_value=0)


def validate_date(value, field_name):
    # Kiểm tra ngày đúng định dạng YYYY-MM-DD
    text = (value or "").strip()
    if not text:
        return None, None
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return None, f"{field_name} must use YYYY-MM-DD format."
    return text, None


def validate_customer_data(full_name, gender, age, city, country, email):
    # Kiểm tra thông tin khách hàng
    full_name = full_name.strip()
    gender = gender.strip()
    city = city.strip()
    country = country.strip() or "Vietnam"
    email = email.strip()
    if not full_name:
        return None, "Full Name is required."
    if gender not in ("Male", "Female"):
        return None, "Gender must be Male or Female."
    age_value, error = parse_int(age, "Age", 18, 100)
    if error:
        return None, "Age must be an integer from 18 to 100."
    if email and "@" not in email:
        return None, "Invalid email. Email must contain @."
    return (full_name, gender, age_value, city, country, email), None


def validate_employee_data(full_name, department, position_name, hire_date):
    # Kiểm tra thông tin nhân viên
    full_name = full_name.strip()
    department = department.strip()
    position_name = position_name.strip()
    if not full_name:
        return None, "Full Name is required."
    if len(full_name) > 100:
        return None, "Full Name must not exceed 100 characters."
    hire_date_value, error = validate_date(hire_date, "Hire Date")
    if error:
        return None, error
    return (full_name, department, position_name, hire_date_value), None


def validate_product_data(product_name, category_name, category_map, price, cost):
    # Kiểm tra thông tin sản phẩm
    product_name = product_name.strip()
    category_name = category_name.strip()
    if not product_name:
        return None, "Product Name is required."
    if category_name not in category_map:
        return None, "Please select a category."
    price_value, error = parse_money(price, "Price")
    if error:
        return None, "Price must be a number >= 0."
    cost_value, error = parse_money(cost, "Cost")
    if error:
        return None, "Cost must be a number >= 0."
    return (product_name, category_map[category_name], price_value, cost_value), None


def validate_category_data(category_name):
    # Kiểm tra thông tin danh mục
    category_name = category_name.strip()
    if not category_name:
        return None, "Category Name is required."
    if len(category_name) > 100:
        return None, "Category Name must not exceed 100 characters."
    return category_name, None


def validate_order_data(
    customer,
    employee,
    product,
    quantity,
    order_date,
    payment_method,
    payment_methods,
    discount,
    payment,
    is_update=False,
    order_id=None,
    order_detail_id=None,
):
    # Kiểm tra dữ liệu đơn hàng trước khi lưu
    if not customer.strip():
        return "Please select a customer."
    if not employee.strip():
        return "Please select an employee."
    if not product.strip():
        return "Please select a product."
    if not str(quantity).strip():
        return "Please enter quantity."
    if not order_date.strip():
        return "Please enter order date."
    _quantity, error = parse_int(quantity, "Quantity", min_value=1)
    if error:
        return "Quantity must be an integer > 0."
    if discount is None:
        return "Discount must be from 0 to 100."
    if payment_method not in payment_methods:
        return "Payment Method must be Cash, Credit Card, Bank Transfer or E-Wallet."
    _date, error = validate_date(order_date, "Order Date")
    if error:
        return error
    payment_value, error = parse_money(payment, "Calculated Payment Amount")
    if error or payment_value < 0:
        return "Calculated Payment Amount is invalid."
    if is_update and not str(order_id or "").strip():
        return "Please select a row to update."
    if is_update and not order_detail_id:
        return "Missing OrderDetailID. Please select a row in the table."
    return None
