# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

import crud
import validators


class EmployeeManagerWindow(tk.Toplevel):
    # Popup quản lý nhân viên
    def __init__(self, parent, on_change=None):
        # Tạo cửa sổ con và biến nhập liệu
        super().__init__(parent)
        self.on_change = on_change
        self.selected_employee_id = None

        self.title("Manage Employees")
        self.geometry("900x540")
        self.transient(parent)

        self.var_full_name = tk.StringVar()
        self.var_department = tk.StringVar()
        self.var_position = tk.StringVar()
        self.var_hire_date = tk.StringVar()

        self._build_form()
        self._build_tree()
        self.load_employees()

    def _build_form(self):
        # Tạo form nhập thông tin nhân viên
        form = ttk.LabelFrame(self, text="Employee Details")
        form.pack(fill=tk.X, padx=10, pady=8)
        fields = ttk.Frame(form)
        fields.pack(fill=tk.X, padx=6, pady=6)
        pad = {"padx": 6, "pady": 4}
        ttk.Label(fields, text="Full Name:").grid(row=0, column=0, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_full_name, width=30).grid(row=0, column=1, sticky=tk.W, **pad)
        ttk.Label(fields, text="Department:").grid(row=0, column=2, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_department, width=24).grid(row=0, column=3, sticky=tk.W, **pad)
        ttk.Label(fields, text="Position:").grid(row=1, column=0, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_position, width=30).grid(row=1, column=1, sticky=tk.W, **pad)
        ttk.Label(fields, text="Hire Date (YYYY-MM-DD):").grid(row=1, column=2, sticky=tk.W, **pad)
        ttk.Entry(fields, textvariable=self.var_hire_date, width=24).grid(row=1, column=3, sticky=tk.W, **pad)

        buttons = ttk.Frame(form)
        buttons.pack(fill=tk.X, padx=6, pady=(0, 6))
        ttk.Button(buttons, text="Add Employee", command=self.add_employee).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Update Employee", command=self.update_employee).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Delete Employee", command=self.delete_employee).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Refresh", command=self.refresh_after_change).pack(side=tk.LEFT, padx=4)

    def _build_tree(self):
        # Tạo bảng danh sách nhân viên
        tree_frame = ttk.LabelFrame(self, text="Employee List")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        columns = ("employee_id", "full_name", "department", "position", "hire_date")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        headers = {"employee_id": "Employee ID", "full_name": "Full Name", "department": "Department", "position": "Position", "hire_date": "Hire Date"}
        widths = {"employee_id": 90, "full_name": 220, "department": 170, "position": 170, "hire_date": 120}
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
        # Kiểm tra dữ liệu trước khi lưu nhân viên
        data, error = validators.validate_employee_data(
            self.var_full_name.get(),
            self.var_department.get(),
            self.var_position.get(),
            self.var_hire_date.get(),
        )
        if error:
            messagebox.showwarning("Invalid Data", error, parent=self)
        return data

    def clear_form(self):
        # Xóa dữ liệu form nhân viên
        self.selected_employee_id = None
        self.var_full_name.set("")
        self.var_department.set("")
        self.var_position.set("")
        self.var_hire_date.set("")
        selected = self.tree.selection()
        if selected:
            self.tree.selection_remove(selected)

    def load_employees(self):
        # Đổ danh sách nhân viên lên bảng
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        try:
            for row in crud.get_all_employees_detail():
                hire_date = row["hire_date"]
                if hasattr(hire_date, "strftime"):
                    hire_date = hire_date.strftime("%Y-%m-%d")
                self.tree.insert("", tk.END, values=(row["employee_id"], row["full_name"], row["department"] or "", row["position_name"] or "", hire_date or ""))
        except Exception as error:
            messagebox.showerror("Load Employees Error", str(error), parent=self)

    def refresh_after_change(self):
        # Refresh popup và báo cho màn hình chính cập nhật combobox
        self.load_employees()
        if self.on_change:
            self.on_change()

    def add_employee(self):
        # Thêm nhân viên mới
        data = self._get_form_data()
        if not data:
            return
        try:
            new_employee_id = crud.insert_employee(*data)
            messagebox.showinfo("Success", f"Employee added successfully.\nEmployee ID = {new_employee_id}", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Add Employee Error", str(error), parent=self)

    def update_employee(self):
        # Cập nhật nhân viên đang chọn
        if not self.selected_employee_id:
            messagebox.showwarning("Invalid Data", "Please select an employee to update.", parent=self)
            return
        data = self._get_form_data()
        if not data:
            return
        try:
            crud.update_employee(self.selected_employee_id, *data)
            messagebox.showinfo("Success", "Employee updated successfully.", parent=self)
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Update Employee Error", str(error), parent=self)

    def delete_employee(self):
        # Xóa nhân viên nếu chưa có đơn hàng
        if not self.selected_employee_id:
            messagebox.showwarning("Invalid Data", "Please select an employee to delete.", parent=self)
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this employee?", parent=self):
            return
        try:
            crud.delete_employee(self.selected_employee_id)
            messagebox.showinfo("Success", "Employee deleted successfully.", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Delete Employee Error", str(error), parent=self)

    def on_select(self, _event=None):
        # Đưa dữ liệu dòng được chọn lên form
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_employee_id = int(values[0])
        self.var_full_name.set(values[1])
        self.var_department.set(values[2])
        self.var_position.set(values[3])
        self.var_hire_date.set(values[4])
