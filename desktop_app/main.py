#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow
from utils.db_handler import DatabaseHandler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from login_form import LoginWindow

class LoginHandler:
    def __init__(self):
        self.login_successful = False
    
    def on_login_success(self):
        self.login_successful = True

def main():
    """Hàm khởi chạy ứng dụng desktop"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Sử dụng style Fusion để giao diện đẹp hơn
    
    # Thiết lập biểu tượng ứng dụng ở cấp độ QApplication
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    icon_path = os.path.join(base_dir, "imgs", "vtn_vip.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # Khởi tạo handler xử lý đăng nhập
    login_handler = LoginHandler()
    
    # Khởi tạo cửa sổ đăng nhập
    login_window = LoginWindow()
    
    # Kết nối tín hiệu đăng nhập thành công
    login_window.login_confirmed_signal = login_handler.on_login_success
    
    # Hiển thị cửa sổ đăng nhập
    login_window.show()
    app.exec()
    
    # Kiểm tra trạng thái đăng nhập
    if login_handler.login_successful:
        print("Đăng nhập thành công, mở ứng dụng chính...")
        # Khởi tạo DatabaseHandler
        db = DatabaseHandler()
        
        # Làm tròn số tiền trong hóa đơn (loại bỏ số thập phân thừa)
        db.lam_tron_so_tien_hoa_don()
        
        # Khởi tạo cửa sổ chính
        window = MainWindow(db)
        window.show()
        
        # Chạy vòng lặp sự kiện cho cửa sổ chính
        return_code = app.exec()
        sys.exit(return_code)
    else:
        print("Đăng nhập thất bại hoặc người dùng đã hủy.")
        sys.exit(0)

if __name__ == "__main__":
    main() 