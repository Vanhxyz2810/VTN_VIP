# Hệ thống kích hoạt thiết bị VTN VIP

## Tổng quan
Hệ thống kích hoạt thiết bị cho ứng dụng VTN VIP giúp đảm bảo rằng chỉ các thiết bị được phép mới có thể sử dụng phần mềm. Hệ thống hoạt động dựa trên mã HWID (Hardware ID) duy nhất của mỗi máy tính.

## Các thành phần chính

### 1. Máy chủ kích hoạt (activate_device_flask.py)
- Máy chủ Flask nhỏ gọn để quản lý và kích hoạt thiết bị
- Giao diện web cho quản trị viên
- API để xác thực thiết bị từ xa
- Lưu trữ và quản lý danh sách thiết bị được phép

### 2. Quản lý thiết bị (manage_device.py)
- Thêm, sửa, xóa thiết bị trong cơ sở dữ liệu
- Quản lý thông tin chi tiết về mỗi thiết bị
- Theo dõi lịch sử kích hoạt
- Cung cấp giao diện quản lý thiết bị

### 3. Cơ sở dữ liệu (devices.db)
- Lưu trữ thông tin về các thiết bị được kích hoạt
- Sử dụng SQLite để dễ dàng triển khai
- Bảo mật thông tin thiết bị

## Quy trình kích hoạt

1. Người dùng chạy ứng dụng và nhận mã HWID
2. Người dùng gửi mã HWID cho quản trị viên
3. Quản trị viên đăng nhập vào hệ thống kích hoạt
4. Quản trị viên thêm thiết bị với mã HWID và thông tin liên quan
5. Hệ thống lưu thông tin vào cơ sở dữ liệu
6. Người dùng khởi động lại ứng dụng và được phép đăng nhập

## Bảo mật

- Mã HWID được tạo từ nhiều thông số phần cứng
- Thông tin thiết bị được mã hóa trong cơ sở dữ liệu
- Hệ thống kiểm tra nhiều yếu tố xác thực
- Chống sao chép và chia sẻ trái phép phần mềm

## Tùy chỉnh và mở rộng

Hệ thống có thể được mở rộng để:
- Hỗ trợ giới hạn thời gian sử dụng
- Kích hoạt tính năng theo gói đăng ký
- Theo dõi thống kê sử dụng
- Tích hợp với hệ thống thanh toán