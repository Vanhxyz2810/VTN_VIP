# Hệ thống đăng nhập VTN VIP

## Tổng quan

Hệ thống đăng nhập VTN VIP được phát triển với các tính năng bảo mật cao, hỗ trợ:

1. Xác thực người dùng
2. Xác thực thiết bị bằng HWID (Hardware ID)
3. Kích hoạt thiết bị thông qua máy chủ Flask

## Các file chính

- `login_form.py`: Form đăng nhập với giao diện người dùng
- `activate_device_flask.py`: Máy chủ Flask để kích hoạt thiết bị
- `manage_device.py`: Quản lý danh sách thiết bị được phép sử dụng
- `devices.db`: Cơ sở dữ liệu SQLite lưu trữ thông tin thiết bị

## Cách hoạt động

1. Khi người dùng khởi động ứng dụng, form đăng nhập hiển thị
2. Hệ thống kiểm tra HWID của thiết bị
3. Nếu thiết bị chưa được kích hoạt, hiển thị tùy chọn kích hoạt
4. Người dùng sao chép HWID và gửi cho quản trị viên
5. Quản trị viên kích hoạt thiết bị qua máy chủ Flask
6. Sau khi thiết bị được kích hoạt, người dùng đăng nhập và sử dụng ứng dụng

## Lớp và hàm chính

- `LoginWindow`: Cửa sổ đăng nhập chính
- `TypingLabel`: Label với hiệu ứng gõ chữ
- `CustomTitleBar`: Thanh tiêu đề tùy chỉnh
- `get_hwid()`: Lấy mã HWID duy nhất của máy
- `create_activation_html()`: Tạo trang HTML để kích hoạt
- `check_activation()`: Kiểm tra trạng thái kích hoạt của thiết bị