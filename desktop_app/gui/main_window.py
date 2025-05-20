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

# Định nghĩa các màu chủ đạo theo phong cách sang trọng
VTN_YELLOW = "#e3b53b"  # Màu vàng gold
VTN_ORANGE = "#d4a82b"  # Màu vàng đậm hơn
VTN_BACKGROUND = "#121212"  # Màu nền đen
VTN_TEXT_YELLOW = "#e3b53b"  # Màu chữ vàng gold
VTN_TEXT_WHITE = "#FFFFFF"  # Màu chữ trắng

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
        header_frame.setStyleSheet(f"background-color: #121212; border-bottom: 2px solid {VTN_YELLOW}; border-radius: 0px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Thêm logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "imgs", "vtn_vip.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            logo_label.setText("VTNVIP")
            logo_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {VTN_TEXT_YELLOW};")
        
        header_layout.addWidget(logo_label)
        
        # Tiêu đề chính
        title_label = QLabel("HỆ THỐNG QUẢN LÝ TIỀN ĐIỆN")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {VTN_TEXT_YELLOW}; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label, 1)  # 1 là stretch factor
        
        # Thêm header vào layout chính
        main_layout.addWidget(header_frame)
        
        # Tạo TabWidget với style mới
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{ 
                border: 1px solid #2c2c2c; 
                border-radius: 5px;
                background-color: #121212; 
            }}
            
            QTabBar::tab {{
                background-color: #2c2c2c;
                border: 1px solid #2c2c2c;
                border-bottom-color: transparent;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
                padding: 8px 15px;
                margin-right: 3px;
                font-weight: bold;
                color: {VTN_TEXT_WHITE};
            }}
            
            QTabBar::tab:selected {{
                background-color: {VTN_YELLOW};
                color: #121212;
            }}
            
            QTabBar::tab:hover {{
                background-color: {VTN_ORANGE};
                color: #121212;
            }}
        """)
        
        # Tạo các tab
        self.khach_hang_tab = KhachHangTab(self.db)
        self.hoa_don_tab = HoaDonTab(self.db)
        self.bang_gia_tab = BangGiaTab(self.db)
        self.thong_ke_tab = ThongKeTab(self.db)
        
        # Thiết lập background màu đen cho các tab
        for tab in [self.khach_hang_tab, self.hoa_don_tab, self.bang_gia_tab, self.thong_ke_tab]:
            tab.setStyleSheet(f"background-color: #121212; color: {VTN_TEXT_WHITE};")
        
        # Thêm các tab vào TabWidget với icon SVG
        # Thêm các tab với icon mặc định
        self.tab_widget.addTab(self.khach_hang_tab, QIcon("../assets/icons/customer_white.svg"), "Khách Hàng")
        self.tab_widget.addTab(self.hoa_don_tab, QIcon("../assets/icons/bill_white.svg"), "Hóa Đơn")
        self.tab_widget.addTab(self.bang_gia_tab, QIcon("../assets/icons/electric_white.svg"), "Bảng Giá Điện") 
        self.tab_widget.addTab(self.thong_ke_tab, QIcon("../assets/icons/chart_white.svg"), "Thống Kê & Báo Cáo")


        def update_tab_icons(index):
            for i in range(self.tab_widget.count()):
                if i == index:
                    if i == 0:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/customer_black.svg"))
                    elif i == 1:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/bill_black.svg"))
                    elif i == 2:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/electric_black.svg"))
                    elif i == 3:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/chart_black.svg"))
                else:
                    # Khôi phục icon mặc định
                    if i == 0:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/customer_white.svg"))
                    elif i == 1:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/bill_white.svg"))
                    elif i == 2:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/electric_white.svg"))
                    elif i == 3:
                        self.tab_widget.setTabIcon(i, QIcon("../assets/icons/chart_white.svg"))

        # Kết nối sự kiện thay đổi tab
        self.tab_widget.currentChanged.connect(update_tab_icons)
        # Cập nhật icon cho tab đầu tiên
        update_tab_icons(0)
        

        # Thêm TabWidget vào layout chính
        main_layout.addWidget(self.tab_widget)
        
        # Tạo thanh trạng thái đẹp hơn
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: #121212; color: {VTN_TEXT_YELLOW}; font-weight: bold; border-top: 1px solid {VTN_YELLOW}; padding: 3px;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Đang xem: Khách Hàng")
        
        # Kết nối sự kiện thay đổi tab
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def set_application_style(self):
        """Thiết lập style chung cho toàn bộ ứng dụng"""
        # Tạo style sheet chung cho toàn bộ ứng dụng
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background-color: {VTN_BACKGROUND};
                color: {VTN_TEXT_WHITE};
            }}
            
            QTabWidget QWidget {{
                background-color: {VTN_BACKGROUND};
            }}
            
            QPushButton {{
                background-color: transparent;
                color: {VTN_TEXT_YELLOW};
                border: 1px solid {VTN_YELLOW};
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {VTN_YELLOW};
                color: #121212;
            }}
            
            QPushButton:pressed {{
                background-color: #a88100;
                color: #121212;
            }}
            
            QPushButton#btnThem, QPushButton#btnSua, QPushButton#btnXoa, QPushButton#btnLamMoi, QPushButton#btnTimKiem {{
                background-color: {VTN_YELLOW};
                color: #121212;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
            }}
            
            QPushButton#btnXoa {{
                background-color: #e74c3c;
                color: #121212;
            }}
            
            QPushButton#btnThem:hover, QPushButton#btnSua:hover, QPushButton#btnLamMoi:hover, QPushButton#btnTimKiem:hover {{
                background-color: #d4a82b;
            }}
            
            QPushButton#btnXoa:hover {{
                background-color: #c0392b;
            }}
            
            QLineEdit, QComboBox, QDateEdit, QSpinBox {{
                border: 1px solid {VTN_YELLOW};
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: #121212;
            }}
            
            QTableView {{
                border: 1px solid #2c2c2c;
                background-color: #121212;
                alternate-background-color: #1a1a1a;
                selection-background-color: {VTN_ORANGE};
                selection-color: #121212;
                color: {VTN_TEXT_WHITE};
                gridline-color: #2c2c2c;
            }}
            
            QTableView::item {{
                padding: 5px;
                border-color: #2c2c2c;
            }}
            
            QTableView::item:selected {{
                background-color: {VTN_YELLOW};
                color: #121212;
            }}
            
            QTableView QTableCornerButton::section {{
                background-color: {VTN_YELLOW};
                border: 1px solid #2c2c2c;
            }}
            
            QHeaderView::section {{
                background-color: {VTN_YELLOW};
                color: #121212;
                padding: 5px;
                border: 1px solid #2c2c2c;
                font-weight: bold;
            }}
            
            QTabWidget::tab-bar {{
                alignment: center;
            }}
            
            QLabel[objectName^="title"] {{
                color: {VTN_TEXT_YELLOW};
                font-weight: bold;
                font-size: 14px;
            }}
            
            QFrame#contentFrame {{
                background-color: #121212;
                border: 1px solid #2c2c2c;
                border-radius: 5px;
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