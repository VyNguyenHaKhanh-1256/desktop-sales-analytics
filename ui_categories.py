# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

import crud
import validators


class CategoryManagerWindow(tk.Toplevel):
    # Popup quản lý danh mục sản phẩm
    def __init__(self, parent, on_change=None):
        # Tạo cửa sổ con và biến nhập liệu
        super().__init__(parent)
        self.on_change = on_change
        self.selected_category_id = None

        self.title("Manage Categories")
        self.geometry("620x440")
        self.transient(parent)

        self.var_category_name = tk.StringVar()
        self._build_form()
        self._build_tree()
        self.load_categories()

    def _build_form(self):
        # Tạo form nhập danh mục
        form = ttk.LabelFrame(self, text="Category Details")
        form.pack(fill=tk.X, padx=10, pady=8)
        ttk.Label(form, text="Category Name:").pack(side=tk.LEFT, padx=6, pady=8)
        ttk.Entry(form, textvariable=self.var_category_name, width=36).pack(side=tk.LEFT, padx=6, pady=8)

        buttons = ttk.Frame(self)
        buttons.pack(fill=tk.X, padx=10, pady=4)
        ttk.Button(buttons, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Update Category", command=self.update_category).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Delete Category", command=self.delete_category).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side=tk.LEFT, padx=4)
        ttk.Button(buttons, text="Refresh", command=self.refresh_after_change).pack(side=tk.LEFT, padx=4)

    def _build_tree(self):
        # Tạo bảng danh sách danh mục
        tree_frame = ttk.LabelFrame(self, text="Category List")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.tree = ttk.Treeview(tree_frame, columns=("category_id", "category_name"), show="headings", selectmode="browse")
        self.tree.heading("category_id", text="Category ID")
        self.tree.heading("category_name", text="Category Name")
        self.tree.column("category_id", width=100, anchor=tk.CENTER)
        self.tree.column("category_name", width=360, anchor=tk.W)
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _get_category_name(self):
        # Kiểm tra tên danh mục trước khi lưu
        category_name, error = validators.validate_category_data(self.var_category_name.get())
        if error:
            messagebox.showwarning("Invalid Data", error, parent=self)
            return None
        current_id = self.selected_category_id
        for row in crud.get_all_categories_detail():
            if row["category_name"].lower() == category_name.lower() and row["category_id"] != current_id:
                messagebox.showwarning("Invalid Data", "This category already exists.", parent=self)
                return None
        return category_name

    def clear_form(self):
        # Xóa dữ liệu form danh mục
        self.selected_category_id = None
        self.var_category_name.set("")
        selected = self.tree.selection()
        if selected:
            self.tree.selection_remove(selected)

    def load_categories(self):
        # Đổ danh sách danh mục lên bảng
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        try:
            for row in crud.get_all_categories_detail():
                self.tree.insert("", tk.END, values=(row["category_id"], row["category_name"]))
        except Exception as error:
            messagebox.showerror("Load Categories Error", str(error), parent=self)

    def refresh_after_change(self):
        # Refresh popup và báo cho màn hình chính cập nhật combobox
        self.load_categories()
        if self.on_change:
            self.on_change()

    def add_category(self):
        # Thêm danh mục mới
        category_name = self._get_category_name()
        if not category_name:
            return
        try:
            crud.insert_category(category_name)
            messagebox.showinfo("Success", "Category added successfully.", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Add Category Error", str(error), parent=self)

    def update_category(self):
        # Cập nhật danh mục đang chọn
        if not self.selected_category_id:
            messagebox.showwarning("Invalid Data", "Please select a category to update.", parent=self)
            return
        category_name = self._get_category_name()
        if not category_name:
            return
        try:
            crud.update_category(self.selected_category_id, category_name)
            messagebox.showinfo("Success", "Category updated successfully.", parent=self)
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Update Category Error", str(error), parent=self)

    def delete_category(self):
        # Xóa danh mục nếu chưa có sản phẩm
        if not self.selected_category_id:
            messagebox.showwarning("Invalid Data", "Please select a category to delete.", parent=self)
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this category?", parent=self):
            return
        try:
            crud.delete_category(self.selected_category_id)
            messagebox.showinfo("Success", "Category deleted successfully.", parent=self)
            self.clear_form()
            self.refresh_after_change()
        except Exception as error:
            messagebox.showerror("Delete Category Error", str(error), parent=self)

    def on_select(self, _event=None):
        # Đưa dữ liệu dòng được chọn lên form
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_category_id = int(values[0])
        self.var_category_name.set(values[1])
