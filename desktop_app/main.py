#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow
from utils.db_handler import DatabaseHandler

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
    
    # Khởi tạo DatabaseHandler
    db = DatabaseHandler()
    
    # Làm tròn số tiền trong hóa đơn (loại bỏ số thập phân thừa)
    db.lam_tron_so_tien_hoa_don()
    
    # Khởi tạo cửa sổ chính
    window = MainWindow(db)
    window.show()
    
    # Chạy vòng lặp sự kiện
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 