import os
import shutil

def center_text(text):
    columns = shutil.get_terminal_size().columns
    return text.center(columns)

os.system('cls' if os.name == 'nt' else 'clear')

print(center_text("VTN VIP"))
print(center_text("QUẢN LÝ ĐIỆN NĂNG CHUYÊN NGHIỆP"))
print()
print(center_text("HỆ THỐNG QUẢN LÝ TIỀN ĐIỆN"))
print()
print(center_text("MENU CHÍNH"))
print(center_text("1. Quản lý khách hàng"))
print(center_text("2. Quản lý hóa đơn"))
print(center_text("3. Quản lý bảng giá điện"))
print(center_text("4. Thống kê và báo cáo"))
print(center_text("0. Thoát"))
print()
print(center_text("Nhập lựa chọn của bạn: "), end='')
