# Ứng Dụng Quản Lý & Phân Tích Dữ Liệu Bán Hàng (Desktop Sales Analytics)

> **Đề tài:** Xây dựng ứng dụng Python Desktop kết nối SQL Server và Tableau để quản lý, phân tích dữ liệu bán hàng.

---

## 📌 Giới thiệu tổng quan

Hệ thống được thiết kế theo quy trình dữ liệu khép kín:
$$\text{Python Desktop App (Tkinter)} \longrightarrow \text{SQL Server (TableauAnalysisDB)} \longrightarrow \text{Tableau Dashboard}$$

- **Python Desktop App:** Đóng vai trò làm giao diện nhập liệu, kiểm tra tính hợp lệ dữ liệu, thực hiện các thao tác CRUD và tính toán KPI/báo cáo nhanh.
- **SQL Server:** Nơi lưu trữ tập trung, đảm bảo tính toàn vẹn và nhất quán dữ liệu giữa các thực thể (Khách hàng, Nhân viên, Sản phẩm, Đơn hàng, Thanh toán).
- **Tableau Desktop:** Kết nối trực tiếp (Live Connection) hoặc qua file xuất dữ liệu CSV để xây dựng Dashboard trực quan hóa hiệu suất kinh doanh (Sales Performance Dashboard).

---

## 🚀 Các tính năng chính

### 1. Quản lý nghiệp vụ bán hàng (Order Management)
- **CRUD Đơn hàng:** Tạo mới, chỉnh sửa, xóa và hiển thị danh sách đơn hàng.
- **Tự động hóa tính toán:** Tự động điền đơn giá sản phẩm và tính thành tiền/thanh toán theo công thức:
  $$\text{Revenue} = \text{Quantity} \times \text{UnitPrice} \times \left(1 - \frac{\text{Discount}}{100}\right)$$
- **Toàn vẹn giao dịch (Transaction & Rollback):** Đảm bảo tính đồng bộ tuyệt đối giữa 3 bảng: `Orders`, `OrderDetails` và `Payments`.

### 2. Quản lý dữ liệu nền (Master Data)
- Hỗ trợ các popup quản lý riêng biệt cho:
  - **Khách hàng (Customers):** Họ tên, giới tính, độ tuổi, thành phố, quốc gia, email.
  - **Nhân viên (Employees):** Họ tên, phòng ban, chức vụ, ngày vào làm.
  - **Sản phẩm (Products):** Tên sản phẩm, danh mục, giá bán, giá vốn (ràng buộc giá bán $\ge$ giá vốn).
  - **Danh mục (Categories):** Phân loại nhóm hàng (Laptop, Mouse, Keyboard, Tablet,...).
- **Ràng buộc khóa ngoại an toàn:** Chặn xóa dữ liệu nền nếu đã phát sinh dữ liệu liên quan trong đơn hàng.

### 3. Tìm kiếm & Lọc nâng cao (Search / Filter)
- Tìm kiếm nhanh theo: `Order ID`, `Customer Name`, `Product Name`.
- Lọc đa điều kiện: Theo khoảng thời gian (`From Date` - `To Date`), theo thành phố (`City`), theo danh mục (`Category`).

### 4. Báo cáo & Phân tích nhanh (Analytics)
- **KPI tổng quan:** Tổng số đơn hàng, tổng doanh thu, tổng khách hàng, sản phẩm bán chạy nhất.
- **Quick Report:** Chuyển đổi xem nhanh giữa 3 báo cáo:
  - *Top Products* (Top sản phẩm bán chạy theo số lượng & doanh thu).
  - *Revenue by City* (Doanh thu theo khu vực địa lý).
  - *Revenue by Month* (Xu hướng doanh thu theo thời gian).

### 5. Tích hợp Tableau
- Hỗ trợ xuất dữ liệu bán hàng đã làm sạch ra thư mục `exports/` dạng CSV có gắn timestamp.
- Khởi chạy nhanh ứng dụng Tableau Desktop trực tiếp từ giao diện Python.
- Tự động phản ánh dữ liệu lên **Sales Performance Dashboard** khi Tableau kết nối Live với SQL Server.

---

## 🛠 Công nghệ sử dụng

| Công nghệ / Thư viện | Mục đích sử dụng |
| :--- | :--- |
| **Python 3.10+** | Ngôn ngữ phát triển logic ứng dụng |
| **Tkinter / ttk** | Thiết kế giao diện đồ họa người dùng (Desktop GUI) |
| **Microsoft SQL Server** | Hệ quản trị cơ sở dữ liệu quan hệ lưu trữ dữ liệu |
| **pyodbc** | Driver giao tiếp và thực thi SQL giữa Python & SQL Server |
| **pandas** | Chuyển đổi DataFrame và xuất dữ liệu báo cáo ra CSV |
| **Tableau Desktop** | Thiết kế biểu đồ và xây dựng Sales Performance Dashboard |

---

## 🗄 Cấu trúc Cơ sở dữ liệu (`TableauAnalysisDB`)

Database bao gồm 07 bảng chuẩn hóa:
1. `Customers` — Lưu thông tin khách hàng, kiểm tra độ tuổi (18 - 100) và giới tính.
2. `Employees` — Danh sách nhân viên và phòng ban.
3. `Categories` — Danh mục phân loại sản phẩm.
4. `Products` — Thông tin sản phẩm, kiểm tra đơn giá và giá vốn.
5. `Orders` — Đơn đặt hàng tổng quan.
6. `OrderDetails` — Chi tiết từng sản phẩm, số lượng, đơn giá và chiết khấu trong đơn hàng.
7. `Payments` — Lịch sử và phương thức thanh toán (`Cash`, `Credit Card`, `Bank Transfer`, `E-Wallet`).

---

## Demo 
<img width="461" height="249" alt="Screenshot 2026-10-01 192115" src="https://github.com/user-attachments/assets/208c4a9f-76d9-4f3e-9b92-f09e537a2002" />


## 📁 Cấu trúc thư mục dự án

```text
├── root.py               # File chạy chính của chương trình (Entry point)
├── ui.py                 # Giao diện chính (Dashboard, Order Form, Search, KPI)
├── ui_customers.py       # Popup quản lý khách hàng
├── ui_employees.py       # Popup quản lý nhân viên
├── ui_products.py        # Popup quản lý sản phẩm
├── ui_categories.py      # Popup quản lý danh mục sản phẩm
├── validators.py         # Kiểm tra tính hợp lệ của dữ liệu đầu vào
├── crud.py               # Thao tác đọc/ghi/sửa/xóa SQL Server & Transactions
├── connect.py            # Cấu hình connection string & kiểm tra kết nối DB
├── analytics.py          # Tính toán KPI, báo cáo nhanh và xử lý xuất CSV
├── tableau_helper.py     # Hỗ trợ mở Tableau Desktop và thư mục exports
├── requirements.txt      # Danh sách thư viện Python cần cài đặt
├── exports/              # Thư mục lưu trữ file CSV xuất cho Tableau
└── docs/                 # Thư mục chứa tài liệu báo cáo (.pdf)
