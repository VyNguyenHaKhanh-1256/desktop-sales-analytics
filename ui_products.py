# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

import crud
import validators


class ProductManagerWindow(tk.Toplevel):
    # Popup quản lý sản phẩm
    def __init__(self, parent, on_change=None):
        # Tạo cửa sổ con và biến nhập liệu
        super().__init__(parent)
        self.on_change = on_change
        self.selected_product_id = None
        self.category_map = {}

        self.title("Manage Products")
        self.geometry("940x540")
        self.transient(parent)

        self.var_product_name = tk.StringVar()
        self.var_category = tk.StringVar()
        self.var_price = tk.StringVar()
        self.var_cost = tk.StringVar()

        self._build_form()
        self._build_tree()
        self.load_categories()
        self.load_products()

    def _format_money_value(self, amount):
        # Format tiền cho bảng sản phẩm
        amount = float(amount)
        return str(int(amount)) if amount == int(amount) else f"{amount:.2f}"

    def _build_form(self):
        # Tạo form nhập thông tin sản phẩm
        form = ttk.LabelFrame(self, text="Product Details")
        form.pack(fill=tk.X, padx=10, pady=8)
        fields = ttk.Frame(form)
        fields.pack(fill=tk.X, padx=6, pady=6)
        pad = {"padx": 6, "pady": 4}

        ttk.Label(fields, text="Product Name:").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_product_name, width=30).grid(row=0, column=1, sticky=tk.W, **pad)
        ttk.Label(fields, text="Category:").grid(row=0, column=2, sticky=tk.W, **pad)
        self.cmb_category = ttk.Combobox(fields, textvariable=self.var_category, width=24, state="readonly")
        self.cmb_category.grid(row=0, column=3, sticky=tk.W, **pad)
        ttk.Label(fields, text="Price:").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_price, width=30).grid(row=1, column=1, sticky=tk.W, **pad)
        ttk.Label(fields, text="Cost:").grid(row=1, column=2, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_cost, width=26).grid(row=1, column=3, sticky=tk.W, **pad)

        buttons = ttk.Frame(form)
        buttons.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(buttons, text="Add Product", command=self.add_product).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Update Product", command=self.update_product).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Delete Product", command=self.delete_product).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Refresh", command=self.refresh_after_change).pack(side=tk.LEFT, padx=4)

    def _build_tree(self):
        # Tạo bảng danh sách sản phẩm
        tree_frame = ttk.LabelFrame(self, text="Product List")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        columns = ("product_id", "product_name", "category_name", "price", "cost")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        headers = {"product_id": "Product ID", "product_name": "Product Name", "category_name": "Category Name", "price": "Price", "cost": "Cost"}
        widths = {"product_id": 90, "product_name": 240, "category_name": 190, "price": 130, "cost": 130}
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor=tk.CENTER)
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_categories(self):
        # Tải danh mục vào combobox
        categories = crud.get_categories()
        self.category_map = {name: cid for cid, name in categories}
        self.cmb_category["values"] = list(self.category_map.keys())

    def _get_form_data(self):
        # Kiểm tra dữ liệu trước khi lưu sản phẩm
        data, error = validators.validate_product_data(
            self.var_product_name.get(),
            self.var_category.get(),
            self.category_map,
            self.var_price.get(),
            self.var_cost.get(),
        )
        if error:
            messagebox.showwarning("Invalid Data", error, parent=self)
            return None
        if data[3] > data[2]:
            # Cho phép lưu lỗ nếu người dùng xác nhận
            confirm = messagebox.askyesno("Confirm Save", "Cost is greater than price. Do you want to save anyway?", parent=self)
            if not confirm:
                return None
        return data

    def clear_form(self):
        # Xóa dữ liệu form sản phẩm
        self.selected_product_id = None
        self.var_product_name.set("")
        self.var_category.set("")
        self.var_price.set("")
        self.var_cost.set("")
        selected = self.tree.selection()
        if selected:
            self.tree.selection_remove(selected)

    def load_products(self):
        # Đổ danh sách sản phẩm lên bảng
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        try:
            for row in crud.get_all_products_detail():
                self.tree.insert(
                    "",
                    tk.END,
                    values=(row["product_id"], row["product_name"], row["category_name"], self._format_money_value(row["price"]), self._format_money_value(row["cost"])),
                    tags=(str(row["category_id"]),),
                )
        except Exception as error:
            messagebox.showerror("Load Products Error", str(error), parent=self)

    def refresh_after_change(self):
        # Refresh popup và báo cho màn hình chính cập nhật combobox
        self.load_categories()
        self.load_products()
        if self.on_change:
            self.on_change()

    def add_product(self):
        # Thêm sản phẩm mới
        data = self._get_form_data()
        if not data:
            return
        try:
            new_product_id = crud.insert_product(*data)
            messagebox.showinfo("Success", f"Product added successfully.\nProduct ID = {new_product_id}", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Add Product Error", str(error), parent=self)

    def update_product(self):
        # Cập nhật sản phẩm đang chọn
        if not self.selected_product_id:
            messagebox.showwarning("Invalid Data", "Please select a product to update.", parent=self)
            return
        data = self._get_form_data()
        if not data:
            return
        try:
            crud.update_product(self.selected_product_id, *data)
            messagebox.showinfo("Success", "Product updated successfully.", parent=self)
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Update Product Error", str(error), parent=self)

    def delete_product(self):
        # Xóa sản phẩm nếu chưa phát sinh đơn hàng
        if not self.selected_product_id:
            messagebox.showwarning("Invalid Data", "Please select a product to delete.", parent=self)
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?", parent=self):
            return
        try:
            crud.delete_product(self.selected_product_id)
            messagebox.showinfo("Success", "Product deleted successfully.", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Delete Product Error", str(error), parent=self)

    def on_select(self, _event=None):
        # Đưa dữ liệu dòng được chọn lên form
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        tags = self.tree.item(selected[0], "tags")
        self.selected_product_id = int(values[0])
        self.var_product_name.set(values[1])
        self.var_category.set(values[2])
        self.var_price.set(str(values[3]).replace(",", ""))
        self.var_cost.set(str(values[4]).replace(",", ""))
        if tags:
            category_id = int(tags[0])
            for name, cid in self.category_map.items():
                if cid == category_id:
                    self.var_category.set(name)
                    break
