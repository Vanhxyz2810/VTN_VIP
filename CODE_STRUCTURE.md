# Cấu Trúc Code VTN VIP

## Tổng quan hệ thống

Hệ thống VTN VIP được tổ chức thành các thành phần sau:

1. **Giao diện người dùng đồ họa (GUI)**: Ứng dụng desktop PyQt6
2. **Hệ thống đăng nhập và xác thực**: Quản lý đăng nhập và kích hoạt thiết bị
3. **Hệ thống quản lý dữ liệu**: Xử lý cơ sở dữ liệu và truy vấn
4. **Tiện ích và công cụ**: Các module hỗ trợ và xử lý logic nghiệp vụ
5. **Xuất báo cáo**: Tạo và xuất các báo cáo

## Cấu trúc thư mục

```
├── desktop_app/               # Ứng dụng desktop
│   ├── gui/                   # Thành phần giao diện
│   │   ├── tabs/              # Các tab chức năng
│   │   ├── widgets/           # Các widget tùy chỉnh
│   │   ├── dialogs/           # Hộp thoại và form
│   │   └── main_window.py     # Cửa sổ chính
│   ├── utils/                 # Tiện ích
│   │   ├── db_handler.py      # Xử lý cơ sở dữ liệu
│   │   ├── exporters.py       # Xuất dữ liệu
│   │   └── validators.py      # Kiểm tra dữ liệu đầu vào
│   ├── models/                # Mô hình dữ liệu
│   └── main.py                # Điểm khởi đầu
├── cmd_app/                   # Ứng dụng dòng lệnh
├── login_form.py              # Hệ thống đăng nhập
├── manage_device.py           # Quản lý thiết bị
├── activate_device_flask.py   # Máy chủ kích hoạt
├── data/                      # Dữ liệu ứng dụng
├── imgs/                      # Hình ảnh và tài nguyên
└── requirements.txt           # Thư viện yêu cầu
```

## Mô tả chi tiết các module

### 1. Login System (login_form.py)

Xử lý đăng nhập và xác thực người dùng với các lớp và hàm chính:

- `LoginWindow`: Cửa sổ đăng nhập
- `TypingLabel`: Label với hiệu ứng gõ chữ
- `CustomTitleBar`: Thanh tiêu đề tùy chỉnh
- `get_hwid()`: Lấy HWID duy nhất
- `check_activation()`: Kiểm tra trạng thái kích hoạt
- `on_login_clicked()`: Xử lý sự kiện đăng nhập

### 2. Device Management (manage_device.py)

Quản lý thiết bị được phép sử dụng ứng dụng:

- `DeviceManager`: Lớp chính quản lý thiết bị
- `add_device()`: Thêm thiết bị mới
- `update_device()`: Cập nhật thông tin thiết bị
- `remove_device()`: Xóa thiết bị
- `check_device_in_db()`: Kiểm tra thiết bị trong cơ sở dữ liệu
- `get_device_history()`: Lấy lịch sử kích hoạt

### 3. Activation Server (activate_device_flask.py)

Máy chủ Flask để kích hoạt thiết bị từ xa:

- `app`: Ứng dụng Flask
- `/activate`: Route xử lý kích hoạt
- `/devices`: Route quản lý thiết bị
- `activate_device()`: Kích hoạt thiết bị
- `get_devices()`: Lấy danh sách thiết bị
- `check_activation_status()`: Kiểm tra trạng thái kích hoạt

### 4. Database Handler (desktop_app/utils/db_handler.py)

Xử lý tương tác với cơ sở dữ liệu:

- `DatabaseHandler`: Lớp chính xử lý CSDL
- `connect()`: Kết nối đến CSDL
- `execute_query()`: Thực thi truy vấn
- `fetch_data()`: Lấy dữ liệu
- `lam_tron_so_tien_hoa_don()`: Làm tròn số tiền
- `calculate_electricity_bill()`: Tính hóa đơn tiền điện

### 5. Main Application (desktop_app/main.py)

Điểm khởi đầu của ứng dụng:

- `main()`: Hàm chính khởi chạy ứng dụng
- `LoginHandler`: Xử lý trạng thái đăng nhập

### 6. GUI Components (desktop_app/gui/)

Các thành phần giao diện người dùng:

- `MainWindow`: Cửa sổ chính của ứng dụng
- `CustomerTab`: Tab quản lý khách hàng
- `BillingTab`: Tab quản lý hóa đơn
- `ReportTab`: Tab báo cáo và thống kê
- `SettingsTab`: Tab cài đặt

## Luồng dữ liệu

1. Người dùng đăng nhập qua `login_form.py`
2. Kiểm tra kích hoạt thiết bị thông qua `manage_device.py`
3. Nếu hợp lệ, khởi chạy ứng dụng chính qua `desktop_app/main.py`
4. Tương tác với cơ sở dữ liệu thông qua `db_handler.py`
5. Hiển thị dữ liệu và xử lý tương tác qua các thành phần GUI

## Quy ước và tiêu chuẩn code

- **Đặt tên**: snake_case cho biến và hàm, PascalCase cho lớp
- **Docstring**: Sử dụng định dạng Google style
- **Ngôn ngữ UI**: Tiếng Việt có dấu trong giao diện người dùng
- **Ngôn ngữ Code**: Tiếng Việt không dấu cho tên file và biến
- **Chuẩn mã nguồn**: Tuân thủ PEP 8