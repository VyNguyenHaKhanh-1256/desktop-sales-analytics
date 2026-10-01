# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

import crud
import validators


class CustomerManagerWindow(tk.Toplevel):
    # Popup quản lý khách hàng
    def __init__(self, parent, on_change=None):
        # Tạo cửa sổ con và biến nhập liệu
        super().__init__(parent)
        self.on_change = on_change
        self.selected_customer_id = None

        self.title("Manage Customers")
        self.geometry("980x560")
        self.transient(parent)

        self.var_full_name = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_age = tk.StringVar()
        self.var_city = tk.StringVar()
        self.var_country = tk.StringVar(value="Vietnam")
        self.var_email = tk.StringVar()

        self._build_form()
        self._build_tree()
        self.load_customers()

    def _build_form(self):
        # Tạo form nhập thông tin khách hàng
        form = ttk.LabelFrame(self, text="Customer Details")
        form.pack(fill=tk.X, padx=10, pady=8)
        fields = ttk.Frame(form)
        fields.pack(fill=tk.X, padx=6, pady=6)
        pad = {"padx": 6, "pady": 4}

        ttk.Label(fields, text="Full Name:").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_full_name, width=30).grid(row=0, column=1, sticky=tk.W, **pad)
        ttk.Label(fields, text="Gender:").grid(row=0, column=2, sticky=tk.W, **pad)
        ttk.Combobox(fields, textvariable=self.var_gender, values=("Male", "Female"), width=18, state="readonly").grid(row=0, column=3, sticky=tk.W, **pad)
        ttk.Label(fields, text="Age:").grid(row=0, column=4, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_age, width=12).grid(row=0, column=5, sticky=tk.W, **pad)
        ttk.Label(fields, text="City:").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_city, width=30).grid(row=1, column=1, sticky=tk.W, **pad)
        ttk.Label(fields, text="Country:").grid(row=1, column=2, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_country, width=20).grid(row=1, column=3, sticky=tk.W, **pad)
        ttk.Label(fields, text="Email:").grid(row=1, column=4, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_email, width=28).grid(row=1, column=5, sticky=tk.W, **pad)

        buttons = ttk.Frame(form)
        buttons.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(buttons, text="Add Customer", command=self.add_customer).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Update Customer", command=self.update_customer).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Delete Customer", command=self.delete_customer).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Refresh", command=self.refresh_after_change).pack(side=tk.LEFT, padx=4)

    def _build_tree(self):
        # Tạo bảng danh sách khách hàng
        tree_frame = ttk.LabelFrame(self, text="Customer List")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        columns = ("customer_id", "full_name", "gender", "age", "city", "country", "email")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        headers = {
            "customer_id": "Customer ID",
            "full_name": "Full Name",
            "gender": "Gender",
            "age": "Age",
            "city": "City",
            "country": "Country",
            "email": "Email",
        }
        widths = {"customer_id": 90, "full_name": 190, "gender": 90, "age": 70, "city": 130, "country": 130, "email": 190}
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

    def _get_form_data(self):
        # Kiểm tra dữ liệu trước khi lưu khách hàng
        data, error = validators.validate_customer_data(
            self.var_full_name.get(),
            self.var_gender.get(),
            self.var_age.get(),
            self.var_city.get(),
            self.var_country.get(),
            self.var_email.get(),
        )
        if error:
            messagebox.showwarning("Invalid Data", error, parent=self)
        return data

    def clear_form(self):
        # Xóa dữ liệu form khách hàng
        self.selected_customer_id = None
        self.var_full_name.set("")
        self.var_gender.set("")
        self.var_age.set("")
        self.var_city.set("")
        self.var_country.set("Vietnam")
        self.var_email.set("")
        selected = self.tree.selection()
        if selected:
            self.tree.selection_remove(selected)

    def load_customers(self):
        # Đổ danh sách khách hàng lên bảng
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        try:
            for row in crud.get_all_customers_detail():
                self.tree.insert("", tk.END, values=(row["customer_id"], row["full_name"], row["gender"], row["age"], row["city"] or "", row["country"] or "", row["email"] or ""))
        except Exception as error:
            messagebox.showerror("Load Customers Error", str(error), parent=self)

    def refresh_after_change(self):
        # Refresh popup và báo cho màn hình chính cập nhật combobox
        self.load_customers()
        if self.on_change:
            self.on_change()

    def add_customer(self):
        # Thêm khách hàng mới
        data = self._get_form_data()
        if not data:
            return
        try:
            new_customer_id = crud.insert_customer(*data)
            messagebox.showinfo("Success", f"Customer added successfully.\nCustomer ID = {new_customer_id}", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Add Customer Error", str(error), parent=self)

    def update_customer(self):
        # Cập nhật khách hàng đang chọn
        if not self.selected_customer_id:
            messagebox.showwarning("Invalid Data", "Please select a customer to update.", parent=self)
            return
        data = self._get_form_data()
        if not data:
            return
        try:
            crud.update_customer(self.selected_customer_id, *data)
            messagebox.showinfo("Success", "Customer updated successfully.", parent=self)
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Update Customer Error", str(error), parent=self)

    def delete_customer(self):
        # Xóa khách hàng nếu chưa có đơn hàng
        if not self.selected_customer_id:
            messagebox.showwarning("Invalid Data", "Please select a customer to delete.", parent=self)
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this customer?", parent=self):
            return
        try:
            crud.delete_customer(self.selected_customer_id)
            messagebox.showinfo("Success", "Customer deleted successfully.", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Delete Customer Error", str(error), parent=self)

    def on_select(self, _event=None):
        # Đưa dữ liệu dòng được chọn lên form
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_customer_id = int(values[0])
        self.var_full_name.set(values[1])
        self.var_gender.set(values[2])
        self.var_age.set(values[3])
        self.var_city.set(values[4])
        self.var_country.set(values[5] or "Vietnam")
        self.var_email.set(values[6])
