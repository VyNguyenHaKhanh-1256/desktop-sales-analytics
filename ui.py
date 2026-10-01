# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import traceback

import analytics
import crud
import tableau_helper
import validators
from connect import test_connection
from ui_categories import CategoryManagerWindow
from ui_customers import CustomerManagerWindow
from ui_employees import EmployeeManagerWindow
from ui_products import ProductManagerWindow

PAYMENT_METHODS = ("Cash", "Credit Card", "Bank Transfer", "E-Wallet")


class TableauAnalysisDB(tk.Tk):
    # Cửa sổ chính của ứng dụng
    def __init__(self):
        # Khởi tạo giao diện và dữ liệu ban đầu
        super().__init__()

        self.title("Sales Management - SQL Server + Tableau")
        self.geometry("1280x860")

        self.selected_order_detail_id = None
        self.selected_customer_id = None
        self.selected_employee_id = None
        self.selected_product_id = None

        self.customer_map = {}
        self.employee_map = {}
        self.product_map = {}

        self._init_variables()
        self._build_form()
        self._build_buttons()
        self._build_search()
        self._build_analysis_tableau()
        self._build_treeview()
        self._build_status_bar()

        self._load_combobox_data()
        self.refresh_data()
        self.refresh_analysis()

    def _init_variables(self):
        # Khai báo biến dùng chung cho form và filter
        self.var_order_id = tk.StringVar()
        self.var_customer = tk.StringVar()
        self.var_employee = tk.StringVar()
        self.var_product = tk.StringVar()
        self.var_quantity = tk.StringVar()
        self.var_price = tk.StringVar()
        self.var_discount = tk.StringVar(value="0")
        self.var_order_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.var_payment_method = tk.StringVar(value="Cash")
        self.var_payment = tk.StringVar()

        self.var_quantity.trace_add("write", self._on_amount_input_changed)
        self.var_discount.trace_add("write", self._on_amount_input_changed)

        self.var_search_type = tk.StringVar(value="order_id")
        self.var_search_keyword = tk.StringVar()
        self.var_from_date = tk.StringVar()
        self.var_to_date = tk.StringVar()
        self.var_filter_city = tk.StringVar(value="All")
        self.var_filter_category = tk.StringVar(value="All")
        self.filter_category_map = {}
        self.var_analysis_view = tk.StringVar(value="top_products")

    def _build_form(self):
        # Tạo form nhập và sửa đơn hàng
        container = ttk.Frame(self)
        container.pack(fill=tk.X, padx=10, pady=8)

        frame = ttk.LabelFrame(container, text="Order Form")
        frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        master_frame = ttk.LabelFrame(container, text="Master Data")
        master_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        pad = {"padx": 8, "pady": 5}

        ttk.Label(frame, text="Order ID:").grid(row=0, column=0, sticky=tk.W, **pad)
        self.entry_order_id = ttk.Entry(
            frame, textvariable=self.var_order_id, width=32, state="readonly"
        )
        self.entry_order_id.grid(row=0, column=1, sticky=tk.W, **pad)

        ttk.Label(frame, text="Customer:").grid(row=0, column=2, sticky=tk.W, **pad)
        self.cmb_customer = ttk.Combobox(
            frame, textvariable=self.var_customer, width=30, state="readonly"
        )
        self.cmb_customer.grid(row=0, column=3, sticky=tk.W, **pad)

        ttk.Label(frame, text="Employee:").grid(row=1, column=0, sticky=tk.W, **pad)
        self.cmb_employee = ttk.Combobox(
            frame, textvariable=self.var_employee, width=32, state="readonly"
        )
        self.cmb_employee.grid(row=1, column=1, sticky=tk.W, **pad)

        ttk.Label(frame, text="Product:").grid(row=1, column=2, sticky=tk.W, **pad)
        self.cmb_product = ttk.Combobox(
            frame, textvariable=self.var_product, width=30, state="readonly"
        )
        self.cmb_product.grid(row=1, column=3, sticky=tk.W, **pad)
        self.cmb_product.bind("<<ComboboxSelected>>", self._on_product_selected)

        ttk.Label(frame, text="Quantity:").grid(row=2, column=0, sticky=tk.W, **pad)
        ttk.Entry(frame, textvariable=self.var_quantity, width=34).grid(
            row=2, column=1, sticky=tk.W, **pad
        )

        ttk.Label(frame, text="Price:").grid(row=2, column=2, sticky=tk.W, **pad)
        self.entry_price = ttk.Entry(
            frame, textvariable=self.var_price, width=32, state="readonly"
        )
        self.entry_price.grid(row=2, column=3, sticky=tk.W, **pad)

        ttk.Label(frame, text="Discount (%):").grid(row=3, column=0, sticky=tk.W, **pad)
        ttk.Entry(frame, textvariable=self.var_discount, width=34).grid(
            row=3, column=1, sticky=tk.W, **pad
        )

        ttk.Label(frame, text="Payment Method:").grid(
            row=3, column=2, sticky=tk.W, **pad
        )
        self.cmb_payment_method = ttk.Combobox(
            frame,
            textvariable=self.var_payment_method,
            values=PAYMENT_METHODS,
            width=30,
            state="readonly",
        )
        self.cmb_payment_method.grid(row=3, column=3, sticky=tk.W, **pad)

        ttk.Label(frame, text="Order Date (YYYY-MM-DD):").grid(
            row=4, column=0, sticky=tk.W, **pad
        )
        ttk.Entry(frame, textvariable=self.var_order_date, width=34).grid(
            row=4, column=1, sticky=tk.W, **pad
        )

        ttk.Label(frame, text="Payment Amount:").grid(
            row=4, column=2, sticky=tk.W, **pad
        )
        self.entry_payment = ttk.Entry(
            frame, textvariable=self.var_payment, width=32, state="readonly"
        )
        self.entry_payment.grid(row=4, column=3, sticky=tk.W, **pad)

        master_buttons = [
            # Tạo nhóm nút quản lý dữ liệu nền
            ("Manage Customers", self.open_customer_manager),
            ("Manage Employees", self.open_employee_manager),
            ("Manage Products", self.open_product_manager),
            ("Manage Categories", self.open_category_manager),
        ]
        for index, (text, command) in enumerate(master_buttons):
            ttk.Button(master_frame, text=text, command=command, width=20).grid(
                row=index // 2,
                column=index % 2,
                sticky=tk.EW,
                padx=6,
                pady=5,
            )
        master_frame.columnconfigure(0, weight=1)
        master_frame.columnconfigure(1, weight=1)

    def _build_buttons(self):
        # Tạo các nút thao tác đơn hàng
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=4)

        buttons = [
            ("Add Order", self.add_order),
            ("Update Order", self.update_order),
            ("Delete Order", self.delete_order),
            ("Clear Form", self.clear_form),
            ("Refresh Data", self.refresh_data),
            ("Test DB", self.test_db_connection),
        ]
        for text, command in buttons:
            ttk.Button(frame, text=text, command=command).pack(
                side=tk.LEFT, padx=5, pady=2
            )

    def _build_search(self):
        # Tạo khu vực tìm kiếm và lọc nâng cao
        frame = ttk.LabelFrame(self, text="Search / Filter")
        frame.pack(fill=tk.X, padx=10, pady=6)

        ttk.Label(frame, text="Search by:").grid(row=0, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Radiobutton(frame, text="Order ID", variable=self.var_search_type, value="order_id").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(frame, text="Customer Name", variable=self.var_search_type, value="customer").grid(row=0, column=2, sticky=tk.W)
        ttk.Radiobutton(frame, text="Product Name", variable=self.var_search_type, value="product").grid(row=0, column=3, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.var_search_keyword, width=32).grid(row=0, column=4, padx=8, pady=4, sticky=tk.W)
        ttk.Button(frame, text="Search", command=self.search_data).grid(row=0, column=5, padx=4, pady=4)
        ttk.Button(frame, text="Show All", command=self.refresh_data).grid(row=0, column=6, padx=4, pady=4)

        ttk.Label(frame, text="From Date:").grid(row=1, column=0, sticky=tk.W, padx=6, pady=4)
        ttk.Entry(frame, textvariable=self.var_from_date, width=14).grid(row=1, column=1, sticky=tk.W, pady=4)
        ttk.Label(frame, text="To Date:").grid(row=1, column=2, sticky=tk.W, padx=6, pady=4)
        ttk.Entry(frame, textvariable=self.var_to_date, width=14).grid(row=1, column=3, sticky=tk.W, pady=4)
        ttk.Label(frame, text="City:").grid(row=1, column=4, sticky=tk.E, padx=6, pady=4)
        self.cmb_filter_city = ttk.Combobox(frame, textvariable=self.var_filter_city, width=20, state="readonly")
        self.cmb_filter_city.grid(row=1, column=5, sticky=tk.W, pady=4)
        ttk.Label(frame, text="Category:").grid(row=1, column=6, sticky=tk.E, padx=6, pady=4)
        self.cmb_filter_category = ttk.Combobox(frame, textvariable=self.var_filter_category, width=22, state="readonly")
        self.cmb_filter_category.grid(row=1, column=7, sticky=tk.W, pady=4)
        ttk.Button(frame, text="Apply Filter", command=self.apply_advanced_filter).grid(row=1, column=8, padx=4, pady=4)
        ttk.Button(frame, text="Clear Filter", command=self.clear_filter).grid(row=1, column=9, padx=4, pady=4)

    def _build_analysis_tableau(self):
        # Tạo khu vực phân tích nhanh
        frame = ttk.LabelFrame(self, text="Analytics")
        frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=6)

        kpi = ttk.Frame(frame)
        kpi.pack(fill=tk.X, padx=6, pady=4)
        self.lbl_kpi_orders = ttk.Label(kpi, text="Total Orders: -")
        self.lbl_kpi_revenue = ttk.Label(kpi, text="Revenue: -")
        self.lbl_kpi_customers = ttk.Label(kpi, text="Customers: -")
        self.lbl_kpi_top_product = ttk.Label(kpi, text="Best Seller: -")
        self.lbl_kpi_orders.pack(side=tk.LEFT, padx=12)
        self.lbl_kpi_revenue.pack(side=tk.LEFT, padx=12)
        self.lbl_kpi_customers.pack(side=tk.LEFT, padx=12)
        self.lbl_kpi_top_product.pack(side=tk.LEFT, padx=12)

        body = ttk.Frame(frame)
        body.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        left = ttk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(left, text="Quick Report:").pack(anchor=tk.W)
        mode_frame = ttk.Frame(left)
        mode_frame.pack(fill=tk.X, pady=2)
        ttk.Radiobutton(
            mode_frame,
            text="Top Products",
            variable=self.var_analysis_view,
            value="top_products",
            command=self.refresh_analysis,
        ).pack(side=tk.LEFT)
        ttk.Radiobutton(
            mode_frame,
            text="Revenue by City",
            variable=self.var_analysis_view,
            value="revenue_city",
            command=self.refresh_analysis,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(
            mode_frame,
            text="Revenue by Month",
            variable=self.var_analysis_view,
            value="revenue_month",
            command=self.refresh_analysis,
        ).pack(side=tk.LEFT)

        cols = ("col1", "col2", "col3")
        self.analysis_tree = ttk.Treeview(left, columns=cols, show="headings", height=5)
        for c in cols:
            self.analysis_tree.heading(c, text=c)
            self.analysis_tree.column(c, width=160, anchor=tk.CENTER)
        self.analysis_tree.pack(fill=tk.BOTH, expand=True, pady=4)

        right = ttk.Frame(body)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        # Các nút liên quan Tableau và export
        ttk.Label(right, text="Tableau:").pack(
            anchor=tk.W, pady=(0, 6)
        )
        tableau_btns = [
            ("Refresh Analytics", self.refresh_analysis),
            ("Export CSV", self.export_tableau_csv),
            ("Open Tableau", self.open_tableau_app),
            ("Open Export Folder", self.open_export_folder),
        ]
        for text, cmd in tableau_btns:
            ttk.Button(right, text=text, command=cmd, width=22).pack(fill=tk.X, pady=3)
        ttk.Label(
            right,
            text="Refresh Tableau after CRUD",
            wraplength=200,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=8)

    def _build_treeview(self):
        # Đổ dữ liệu lên Order List
        container = ttk.LabelFrame(self, text="Order List")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        columns = (
            "order_id",
            "customer",
            "employee",
            "product",
            "quantity",
            "price",
            "discount",
            "payment_method",
            "payment",
            "order_date",
        )
        self.tree = ttk.Treeview(
            container, columns=columns, show="headings", selectmode="browse", height=14
        )
        headers = {
            "order_id": "Order ID",
            "customer": "Customer",
            "employee": "Employee",
            "product": "Product",
            "quantity": "Quantity",
            "price": "Price",
            "discount": "Discount",
            "payment_method": "Payment Method",
            "payment": "Payment Amount",
            "order_date": "Order Date",
        }
        widths = {
            "order_id": 80,
            "customer": 150,
            "employee": 130,
            "product": 150,
            "quantity": 80,
            "price": 100,
            "discount": 80,
            "payment_method": 130,
            "payment": 120,
            "order_date": 110,
        }
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor=tk.CENTER)

        scroll_y = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def _build_status_bar(self):
        # Dòng mô tả ngắn luồng dữ liệu của app
        ttk.Label(
            self,
            text="Tkinter -> SQL Server (TableauAnalysisDB) -> vw_SalesForTableau -> Tableau Dashboard (Refresh)",
        ).pack(fill=tk.X, padx=10, pady=4)

    def _load_combobox_data(self):
        # Tải dữ liệu vào combobox
        try:
            self.refresh_customer_combobox()

            self.refresh_employee_combobox()
            self.refresh_product_combobox()
            self._load_filter_data()
        except Exception as error:
            messagebox.showerror(
                "Load Combobox Error",
                f"Cannot connect to SQL Server.\n\n{error}",
            )

    def refresh_customer_combobox(self):
        # Refresh combobox khách hàng
        current_customer = self.var_customer.get()
        customers = crud.get_customers()
        self.customer_map = {name: cid for cid, name in customers}
        self.cmb_customer["values"] = list(self.customer_map.keys())
        if current_customer in self.customer_map:
            self.var_customer.set(current_customer)
        else:
            self.var_customer.set("")

    def refresh_employee_combobox(self):
        # Refresh combobox nhân viên
        current_employee = self.var_employee.get()
        employees = crud.get_employees()
        self.employee_map = {name: eid for eid, name in employees}
        self.cmb_employee["values"] = list(self.employee_map.keys())
        if current_employee in self.employee_map:
            self.var_employee.set(current_employee)
        else:
            self.var_employee.set("")

    def _load_filter_data(self):
        # Tải dữ liệu cho bộ lọc nâng cao
        cities = ["All"] + crud.get_distinct_customer_cities()
        self.cmb_filter_city["values"] = cities
        if self.var_filter_city.get() not in cities:
            self.var_filter_city.set("All")

        categories = crud.get_categories()
        self.filter_category_map = {"All": None}
        self.filter_category_map.update({name: cid for cid, name in categories})
        category_values = list(self.filter_category_map.keys())
        self.cmb_filter_category["values"] = category_values
        if self.var_filter_category.get() not in category_values:
            self.var_filter_category.set("All")

    def refresh_product_combobox(self):
        # Refresh combobox sản phẩm và giá
        current_product = self.var_product.get()
        products = crud.get_products()
        self.product_map = {name: (pid, price) for pid, name, price in products}
        self.cmb_product["values"] = list(self.product_map.keys())
        if current_product in self.product_map:
            self.var_product.set(current_product)
            self._set_price_for_current_product()
        else:
            self.var_product.set("")
            self.var_price.set("")
            self.var_payment.set("")

    def _set_price_for_current_product(self):
        # Tự điền giá khi chọn sản phẩm
        product_name = self.var_product.get()
        if product_name in self.product_map:
            _product_id, price = self.product_map[product_name]
            self.var_price.set(self._format_money_value(price))

    def _on_product_selected(self, _event=None):
        # Khi đổi sản phẩm thì tính lại tiền
        self._set_price_for_current_product()
        self._update_payment_amount()

    def _on_amount_input_changed(self, *_args):
        # Tự tính Payment Amount khi dữ liệu thay đổi
        self._update_payment_amount()

    def _format_money_value(self, amount):
        # Format tiền cho gọn khi hiển thị
        amount = float(amount)
        return str(int(amount)) if amount == int(amount) else f"{amount:.2f}"

    def _parse_discount_value(self, show_warning=False):
        # Kiểm tra giảm giá trong khoảng 0-100
        text = self.var_discount.get().strip()
        if text == "":
            return 0.0
        try:
            discount = float(text)
        except ValueError:
            if show_warning:
                messagebox.showwarning("Invalid Data", "Discount must be a number from 0 to 100.")
            return None
        if discount < 0 or discount > 100:
            if show_warning:
                messagebox.showwarning("Invalid Data", "Discount must be from 0 to 100.")
            return None
        return discount

    def _calculate_payment_amount(self):
        # Tính tiền thanh toán theo sản phẩm, số lượng và giảm giá
        product_name = self.var_product.get()
        if product_name not in self.product_map:
            return None

        quantity_text = self.var_quantity.get().strip()
        if not quantity_text:
            return None
        try:
            quantity = int(quantity_text)
            if quantity < 0:
                return None
        except ValueError:
            return None

        discount = self._parse_discount_value(show_warning=False)
        if discount is None:
            return None

        _product_id, unit_price = self.product_map[product_name]
        return quantity * float(unit_price) * (1 - discount / 100)

    def calculate_payment_amount(self):
        # Hàm public để giữ tên dùng bên ngoài nếu cần
        return self._calculate_payment_amount()

    def _update_payment_amount(self):
        # Tự tính Payment Amount
        amount = self._calculate_payment_amount()
        self.var_payment.set("" if amount is None else self._format_money_value(amount))

    def refresh_analysis(self):
        # Refresh KPI và quick report
        try:
            kpi = analytics.get_kpi_summary()
            revenue = float(kpi.get("total_revenue") or 0)
            self.lbl_kpi_orders.config(
                text=f"Total Orders: {int(kpi.get('total_orders') or 0)}"
            )
            self.lbl_kpi_revenue.config(text=f"Revenue: {revenue:,.0f} VND")
            self.lbl_kpi_customers.config(
                text=f"Customers: {int(kpi.get('total_customers') or 0)}"
            )
            self.lbl_kpi_top_product.config(
                text=f"Best Seller: {kpi.get('top_product', '-')} ({kpi.get('top_product_qty', 0)})"
            )

            mode = self.var_analysis_view.get()
            # Xóa bảng report cũ trước khi đổ dữ liệu mới
            for item in self.analysis_tree.get_children():
                self.analysis_tree.delete(item)

            if mode == "top_products":
                self.analysis_tree.heading("col1", text="Product")
                self.analysis_tree.heading("col2", text="Quantity")
                self.analysis_tree.heading("col3", text="Revenue")
                for row in analytics.get_top_products(5):
                    if "product_name" not in row:
                        raise KeyError("missing field product_name")
                    self.analysis_tree.insert(
                        "",
                        tk.END,
                        values=(
                            row["product_name"],
                            row["quantity"],
                            f"{float(row['revenue']):,.0f}",
                        ),
                    )
            elif mode == "revenue_city":
                self.analysis_tree.heading("col1", text="City")
                self.analysis_tree.heading("col2", text="Revenue")
                self.analysis_tree.heading("col3", text="")
                for row in analytics.get_revenue_by_city():
                    if "city" not in row:
                        raise KeyError("missing field city")
                    self.analysis_tree.insert(
                        "",
                        tk.END,
                        values=(row["city"], f"{float(row['revenue']):,.0f}", ""),
                    )
            else:
                self.analysis_tree.heading("col1", text="Year")
                self.analysis_tree.heading("col2", text="Month")
                self.analysis_tree.heading("col3", text="Revenue")
                for row in analytics.get_revenue_by_month():
                    self.analysis_tree.insert(
                        "",
                        tk.END,
                        values=(
                            row["order_year"],
                            row["order_month"],
                            f"{float(row['revenue']):,.0f}",
                        ),
                    )
        except Exception as error:
            traceback.print_exc()
            missing_field = None
            if isinstance(error, KeyError):
                missing_field = str(error).strip("'\"")
            detail = (
                f"Analytics data mapping error: {missing_field}"
                if missing_field
                else str(error)
            )
            messagebox.showerror("Analytics Error", detail)

    def export_tableau_csv(self):
        # Export CSV cho Tableau
        try:
            path = analytics.export_for_tableau()
            messagebox.showinfo(
                "Export CSV",
                f"CSV exported for Tableau:\n{path}\n\n"
                "You can also connect Tableau directly to vw_SalesForTableau.",
            )
        except Exception as error:
            messagebox.showerror("Export CSV Error", str(error))

    def show_tableau_guide(self):
        # Mở cửa sổ hướng dẫn Tableau
        guide = tableau_helper.get_guide_text()
        win = tk.Toplevel(self)
        win.title("Tableau Guide")
        win.geometry("620x480")
        txt = tk.Text(win, wrap=tk.WORD, padx=10, pady=10)
        txt.pack(fill=tk.BOTH, expand=True)
        txt.insert("1.0", guide)
        txt.config(state=tk.DISABLED)
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=8)

    def open_tableau_app(self):
        # Mở Tableau Desktop
        ok, msg = tableau_helper.open_tableau_desktop()
        if ok:
            messagebox.showinfo("Tableau", msg + "\n\nSQL Server Connection")
        else:
            messagebox.showwarning("Tableau", msg)

    def open_export_folder(self):
        # Mở thư mục export CSV
        try:
            folder = tableau_helper.open_exports_folder()
            messagebox.showinfo("Export Folder", folder)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _refresh_after_master_data_change(self):
        # Refresh lại combobox sau khi thêm dữ liệu nền
        self._load_combobox_data()
        self.refresh_analysis()

    def open_customer_manager(self):
        # Mở popup quản lý khách hàng
        CustomerManagerWindow(self, on_change=self._refresh_after_master_data_change)

    def open_employee_manager(self):
        # Mở popup quản lý nhân viên
        EmployeeManagerWindow(self, on_change=self._refresh_after_master_data_change)

    def open_product_manager(self):
        # Mở popup quản lý sản phẩm
        ProductManagerWindow(self, on_change=self._refresh_after_master_data_change)

    def open_category_manager(self):
        # Mở popup quản lý danh mục
        CategoryManagerWindow(self, on_change=self._refresh_after_master_data_change)

    def validate_form(self, is_update=False):
        # Kiểm tra dữ liệu trước khi lưu đơn hàng
        discount = self._parse_discount_value(show_warning=True)
        if discount is None:
            return False

        self._update_payment_amount()
        error = validators.validate_order_data(
            customer=self.var_customer.get(),
            employee=self.var_employee.get(),
            product=self.var_product.get(),
            quantity=self.var_quantity.get(),
            order_date=self.var_order_date.get(),
            payment_method=self.var_payment_method.get(),
            payment_methods=PAYMENT_METHODS,
            discount=discount,
            payment=self.var_payment.get(),
            is_update=is_update,
            order_id=self.var_order_id.get(),
            order_detail_id=self.selected_order_detail_id,
        )
        if error:
            messagebox.showwarning("Invalid Data", error)
            return False
        return True

    def add_order(self):
        # Thêm đơn hàng mới
        if not self.validate_form(is_update=False):
            return
        try:
            new_order_id = crud.insert_order(
                customer_id=self.customer_map[self.var_customer.get()],
                employee_id=self.employee_map[self.var_employee.get()],
                product_id=self.product_map[self.var_product.get()][0],
                quantity=int(self.var_quantity.get()),
                order_date=self.var_order_date.get().strip(),
                payment_method=self.var_payment_method.get(),
                discount=self._parse_discount_value(),
                payment_amount=float(self.var_payment.get()),
            )
            messagebox.showinfo(
                "Success", f"Order added successfully.\nOrder ID = {new_order_id}"
            )
            self.clear_form()
            self.refresh_data()
            self.refresh_analysis()
        except Exception as error:
            messagebox.showerror("Add Error", str(error))

    def update_order(self):
        # Cập nhật đơn hàng đang chọn
        if not self.validate_form(is_update=True):
            return
        try:
            crud.update_order(
                order_id=int(self.var_order_id.get()),
                order_detail_id=self.selected_order_detail_id,
                customer_id=self.customer_map[self.var_customer.get()],
                employee_id=self.employee_map[self.var_employee.get()],
                product_id=self.product_map[self.var_product.get()][0],
                quantity=int(self.var_quantity.get()),
                order_date=self.var_order_date.get().strip(),
                payment_method=self.var_payment_method.get(),
                discount=self._parse_discount_value(),
                payment_amount=float(self.var_payment.get()),
            )
            messagebox.showinfo("Success", "Order updated successfully.")
            self.refresh_data()
            self.refresh_analysis()
        except Exception as error:
            messagebox.showerror("Update Error", str(error))

    def delete_order(self):
        # Xóa đơn hàng đang chọn
        if not self.var_order_id.get().strip() or not self.selected_order_detail_id:
            messagebox.showwarning("Invalid Data", "Please select a row first.")
            return
        confirm = messagebox.askyesno(
            "Confirm Delete", "Are you sure you want to delete this order?"
        )
        if not confirm:
            return
        try:
            crud.delete_order(
                order_id=int(self.var_order_id.get()),
                order_detail_id=self.selected_order_detail_id,
            )
            messagebox.showinfo("Success", "Order deleted successfully.")
            self.clear_form()
            self.refresh_data()
            self.refresh_analysis()
        except Exception as error:
            messagebox.showerror("Delete Error", str(error))

    def clear_form(self):
        # Xóa dữ liệu trên form nhập đơn hàng
        self.var_order_id.set("")
        self.var_customer.set("")
        self.var_employee.set("")
        self.var_product.set("")
        self.var_quantity.set("")
        self.var_price.set("")
        self.var_discount.set("0")
        self.var_order_date.set(datetime.now().strftime("%Y-%m-%d"))
        self.var_payment_method.set("Cash")
        self.var_payment.set("")
        self.selected_order_detail_id = None
        self.selected_customer_id = None
        self.selected_employee_id = None
        self.selected_product_id = None
        selected_items = self.tree.selection()
        if selected_items:
            self.tree.selection_remove(selected_items)

    def refresh_data(self):
        # Refresh lại bảng và analytics
        try:
            self._load_filter_data()
            rows = crud.get_all_orders()
            self._fill_treeview(rows)
            self.refresh_analysis()
        except Exception as error:
            messagebox.showerror("Refresh Error", str(error))

    def search_data(self):
        # Tìm kiếm đơn hàng cơ bản
        try:
            rows = crud.search_orders(
                self.var_search_type.get(), self.var_search_keyword.get()
            )
            self._fill_treeview(rows)
        except Exception as error:
            messagebox.showerror("Search Error", str(error))

    def search_orders(self):
        self.search_data()

    def show_all(self):
        self.refresh_data()

    def _validate_filter_dates(self):
        # Kiểm tra khoảng ngày lọc
        from_date = self.var_from_date.get().strip()
        to_date = self.var_to_date.get().strip()
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
        except ValueError:
            messagebox.showwarning("Invalid Data", "From Date must use YYYY-MM-DD format.")
            return None
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
        except ValueError:
            messagebox.showwarning("Invalid Data", "To Date must use YYYY-MM-DD format.")
            return None
        if from_dt and to_dt and from_dt > to_dt:
            messagebox.showwarning("Invalid Data", "From Date must be before or equal to To Date.")
            return None
        return from_date or None, to_date or None

    def apply_advanced_filter(self):
        # Áp dụng lọc nâng cao cho Order List
        dates = self._validate_filter_dates()
        if dates is None:
            return
        from_date, to_date = dates
        category_name = self.var_filter_category.get()
        city = self.var_filter_city.get()
        try:
            rows = crud.search_orders_advanced(
                keyword=self.var_search_keyword.get(),
                search_by=self.var_search_type.get(),
                from_date=from_date,
                to_date=to_date,
                city=None if city in ("", "All") else city,
                category_id=self.filter_category_map.get(category_name),
            )
            self._fill_treeview(rows)
        except ValueError:
            messagebox.showwarning("Invalid Data", "Order ID must be an integer when filtering by Order ID.")
        except Exception as error:
            messagebox.showerror("Filter Error", str(error))

    def apply_filter(self):
        self.apply_advanced_filter()

    def clear_filter(self):
        # Xóa điều kiện lọc và hiện lại toàn bộ dữ liệu
        self.var_from_date.set("")
        self.var_to_date.set("")
        self.var_filter_city.set("All")
        self.var_filter_category.set("All")
        self.var_search_keyword.set("")
        self.refresh_data()

    def _fill_treeview(self, rows):
        # Đổ dữ liệu lên bảng đơn hàng
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        for row in rows:
            order_date = row["order_date"]
            if hasattr(order_date, "strftime"):
                order_date = order_date.strftime("%Y-%m-%d")
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["order_id"],
                    row["customer_name"],
                    row["employee_name"],
                    row["product_name"],
                    row["quantity"],
                    f"{row['price']:,.0f}",
                    self._format_money_value(row["discount"]),
                    row["payment_method"],
                    f"{row['payment_amount']:,.0f}",
                    order_date,
                ),
                tags=(
                    str(row["order_detail_id"]),
                    str(row["customer_id"]),
                    str(row["employee_id"]),
                    str(row["product_id"]),
                ),
            )

    def on_tree_select(self, _event=None):
        # Khi chọn dòng thì đưa dữ liệu lên form
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        values = self.tree.item(item_id, "values")
        tags = self.tree.item(item_id, "tags")
        self.var_order_id.set(values[0])
        self.var_customer.set(values[1])
        self.var_employee.set(values[2])
        self.var_product.set(values[3])
        self.var_quantity.set(values[4])
        self.var_price.set(str(values[5]).replace(",", ""))
        self.var_discount.set(str(values[6]).replace(",", ""))
        payment_method = values[7] if values[7] in PAYMENT_METHODS else "Cash"
        self.var_payment_method.set(payment_method)
        self.var_payment.set(str(values[8]).replace(",", ""))
        self.var_order_date.set(values[9])
        if len(tags) >= 4:
            self.selected_order_detail_id = int(tags[0])
            self.selected_customer_id = int(tags[1])
            self.selected_employee_id = int(tags[2])
            self.selected_product_id = int(tags[3])

    def test_db_connection(self):
        # Test nhanh kết nối database từ giao diện
        ok, message = test_connection()
        if ok:
            messagebox.showinfo("Database Connection", message)
        else:
            messagebox.showerror("Database Connection", message)

    def test_db(self):
        self.test_db_connection()


def run_app():
    app = TableauAnalysisDB()
    app.mainloop()
