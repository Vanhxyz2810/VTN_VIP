# 📝 Memory File - VTN VIP

Tệp này lưu trữ các quyết định và thay đổi quan trọng trong dự án VTN VIP.

## 🔄 Cập nhật và tính năng mới

### Hệ thống đăng nhập và kích hoạt (23/05/2024)
- Đã thêm hệ thống đăng nhập bảo mật trong `login_form.py`
- Tích hợp hệ thống xác thực HWID cho từng thiết bị
- Sử dụng SQLite để lưu trữ thông tin thiết bị được kích hoạt

### Quản lý thiết bị (23/05/2024)
- Tạo module `manage_device.py` để quản lý thiết bị được phép sử dụng ứng dụng
- Thêm chức năng thêm, sửa, xóa thiết bị
- Lưu trữ lịch sử kích hoạt của từng thiết bị

### Hệ thống kích hoạt trực tuyến (23/05/2024)
- Phát triển `activate_device_flask.py` - máy chủ Flask nhỏ để kích hoạt thiết bị
- Tích hợp giao diện web để quản lý và kích hoạt thiết bị
- Hỗ trợ kích hoạt bởi quản trị viên

### Cấu trúc dự án (23/05/2024)
- Tổ chức lại cấu trúc thư mục, tách biệt GUI và logic
- Thêm thư mục `utils` để lưu trữ các tiện ích
- Phân chia các tab chức năng thành các module riêng biệt

## 🛠️ Vấn đề kỹ thuật đã giải quyết

### Làm tròn số tiền trong hóa đơn (23/05/2024)
- Đã thêm phương thức `lam_tron_so_tien_hoa_don()` trong DatabaseHandler để loại bỏ số thập phân thừa

### Tối ưu hóa hiệu suất (23/05/2024)
- Cải thiện tốc độ tải dữ liệu trong các bảng
- Tối ưu hóa truy vấn SQL trong module `db_handler.py`

## 📋 Quy ước và tiêu chuẩn

### Quy ước đặt tên
- Sử dụng snake_case cho tên biến và hàm
- Sử dụng PascalCase cho tên lớp
- Đặt tên các file và thư mục bằng tiếng Việt không dấu

### Tiêu chuẩn mã nguồn
- Tuân thủ PEP 8 khi viết mã Python
- Thêm docstring cho mỗi lớp và phương thức
- Sử dụng tiếng Việt có dấu trong các thông báo và giao diện người dùng 