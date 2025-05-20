#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QStatusBar, QFrame)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor, QPalette
import os

from gui.tabs.khach_hang_tab import KhachHangTab
from gui.tabs.hoa_don_tab import HoaDonTab
from gui.tabs.bang_gia_tab import BangGiaTab
from gui.tabs.thong_ke_tab import ThongKeTab

# Định nghĩa các màu chủ đạo theo logo VTN
VTN_YELLOW = "#FFB300"  # Màu vàng chính
VTN_ORANGE = "#FF9800"  # Màu cam
VTN_BACKGROUND = "#FFFDE7"  # Màu nền nhạt
VTN_TEXT = "#212121"  # Màu chữ

class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng desktop
    """
    
    def __init__(self, db):
        """
        Khởi tạo cửa sổ chính
        
        Args:
            db (DatabaseHandler): Đối tượng xử lý dữ liệu
        """
        super().__init__()
        
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        """Khởi tạo giao diện người dùng"""
        # Thiết lập cửa sổ chính
        self.setWindowTitle("VTN - Quản Lý Tiền Điện")
        self.setMinimumSize(1200, 700)
        
        # Thiết lập định dạng với palette
        self.set_application_style()
        
        # Tạo widget trung tâm
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Tạo layout chính
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Tạo header đẹp hơn
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {VTN_YELLOW}; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        
        # Thêm logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "imgs", "vtn_vip.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            logo_label.setText("VTN")
            logo_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFF;")
        
        header_layout.addWidget(logo_label)
        
        # Tiêu đề chính
        title_label = QLabel("HỆ THỐNG QUẢN LÝ TIỀN ĐIỆN")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 là stretch factor
        
        # Thêm header vào layout chính
        main_layout.addWidget(header_frame)
        
        # Tạo TabWidget với style mới
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{ 
                border: 1px solid #ddd; 
                border-radius: 5px;
                background-color: white; 
            }}
            
            QTabBar::tab {{
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                border-bottom-color: transparent;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
                padding: 8px 15px;
                margin-right: 3px;
                font-weight: bold;
            }}
            
            QTabBar::tab:selected {{
                background-color: {VTN_YELLOW};
                color: white;
            }}
            
            QTabBar::tab:hover {{
                background-color: {VTN_ORANGE};
                color: white;
            }}
        """)
        
        # Tạo các tab
        self.khach_hang_tab = KhachHangTab(self.db)
        self.hoa_don_tab = HoaDonTab(self.db)
        self.bang_gia_tab = BangGiaTab(self.db)
        self.thong_ke_tab = ThongKeTab(self.db)
        
        # Thêm các tab vào TabWidget
        self.tab_widget.addTab(self.khach_hang_tab, "Khách Hàng")
        self.tab_widget.addTab(self.hoa_don_tab, "Hóa Đơn")
        self.tab_widget.addTab(self.bang_gia_tab, "Bảng Giá Điện")
        self.tab_widget.addTab(self.thong_ke_tab, "Thống Kê & Báo Cáo")
        
        # Thêm TabWidget vào layout chính
        main_layout.addWidget(self.tab_widget)
        
        # Tạo thanh trạng thái đẹp hơn
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: {VTN_YELLOW}; color: white; font-weight: bold;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sẵn sàng")
        
        # Kết nối sự kiện thay đổi tab
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def set_application_style(self):
        """Thiết lập style chung cho toàn bộ ứng dụng"""
        # Tạo style sheet chung cho toàn bộ ứng dụng
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {VTN_BACKGROUND};
                color: {VTN_TEXT};
            }}
            
            QPushButton {{
                background-color: {VTN_YELLOW};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {VTN_ORANGE};
            }}
            
            QPushButton:pressed {{
                background-color: #E65100;
            }}
            
            QLineEdit, QComboBox, QDateEdit, QSpinBox {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }}
            
            QTableView {{
                border: 1px solid #ddd;
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: {VTN_ORANGE};
                selection-color: white;
            }}
            
            QHeaderView::section {{
                background-color: {VTN_YELLOW};
                color: white;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }}
        """)
    
    def on_tab_changed(self, index):
        """
        Xử lý sự kiện khi thay đổi tab
        
        Args:
            index (int): Chỉ số tab được chọn
        """
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"Đang xem: {tab_name}")
        
        # Cập nhật dữ liệu khi chuyển tab
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'load_data'):
            current_tab.load_data() 