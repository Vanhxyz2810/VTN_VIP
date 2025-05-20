#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
                           QFormLayout, QDialog, QMessageBox, QHeaderView, 
                           QFrame, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QColor

import datetime
from models.khach_hang import KhachHang

# Định nghĩa các màu chủ đạo theo logo VTN
VTN_YELLOW = "#FFB300"  # Màu vàng chính
VTN_ORANGE = "#FF9800"  # Màu cam
VTN_BACKGROUND = "#FFFDE7"  # Màu nền nhạt
VTN_TEXT = "#212121"  # Màu chữ
VTN_DARK_BG = "#121212"  # Màu nền tối
VTN_DARKER_BG = "#1E1E1E"  # Màu nền tối hơn cho các panel
VTN_LIGHT_TEXT = "#EEEEEE"  # Màu chữ sáng
VTN_ACCENT = "#FFC107"  # Màu nhấn
VTN_RED = "#D32F2F"  # Màu đỏ cho nút xóa
VTN_RED_HOVER = "#B71C1C"  # Màu đỏ đậm hơn khi hover
VTN_YELLOW_HOVER = "#FFA000"  # Màu vàng đậm hơn khi hover
VTN_GRAY_BORDER = "#555555"  # Màu viền xám đậm

class KhachHangDialog(QDialog):
    """
    Dialog để thêm/sửa thông tin khách hàng
    """
    
    def __init__(self, parent=None, khach_hang=None):
        """
        Khởi tạo dialog
        
        Args:
            parent (QWidget): Widget cha
            khach_hang (KhachHang): Đối tượng khách hàng (None nếu thêm mới)
        """
        super().__init__(parent)
        
        self.khach_hang = khach_hang
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện dialog"""
        # Thiết lập cửa sổ
        title = "Thêm Khách Hàng Mới" if not self.khach_hang else "Sửa Thông Tin Khách Hàng"
        self.setWindowTitle(title)
        self.setMinimumWidth(450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {VTN_DARK_BG};
                border-radius: 10px;
            }}
            QLabel {{
                font-weight: bold;
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto Medium', 'Segoe UI Semibold', 'Arial', sans-serif;
            }}
            QLineEdit {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 6px;
                padding: 10px;
                background-color: {VTN_DARKER_BG};
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton {{
                background-color: {VTN_YELLOW};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
                min-width: 110px;
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {VTN_YELLOW_HOVER};
            }}
            #headerLabel {{
                color: {VTN_ORANGE};
                font-size: 16px;
                padding: 10px;
            }}
        """)
        
        # Layout chính
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {VTN_YELLOW}; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        
        header_label = QLabel(title)
        header_label.setObjectName("headerLabel")
        header_label.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Form layout
        form_frame = QFrame()
        form_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 8px; padding: 15px;")
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        # Các trường nhập liệu
        self.ho_ten_input = QLineEdit()
        self.dia_chi_input = QLineEdit()
        self.so_dien_thoai_input = QLineEdit()
        self.ma_cong_to_input = QLineEdit()
        
        # Thêm các trường vào form
        form_layout.addRow("Họ tên:", self.ho_ten_input)
        form_layout.addRow("Địa chỉ:", self.dia_chi_input)
        form_layout.addRow("Số điện thoại:", self.so_dien_thoai_input)
        form_layout.addRow("Mã công tơ:", self.ma_cong_to_input)
        
        # Thêm form vào layout chính
        layout.addWidget(form_frame)
        
        # Nếu đang sửa thông tin, điền dữ liệu vào các trường
        if self.khach_hang:
            self.ho_ten_input.setText(self.khach_hang.ho_ten)
            self.dia_chi_input.setText(self.khach_hang.dia_chi)
            self.so_dien_thoai_input.setText(self.khach_hang.so_dien_thoai)
            self.ma_cong_to_input.setText(self.khach_hang.ma_cong_to)
        
        # Các nút
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.save_button = QPushButton("Lưu")
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #555; 
                color: {VTN_LIGHT_TEXT};
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
                min-width: 110px;
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: #666;
            }}
        """)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Kết nối các sự kiện
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def get_khach_hang_data(self):
        """
        Lấy dữ liệu khách hàng từ form
        
        Returns:
            dict: Dữ liệu khách hàng
        """
        if self.khach_hang:
            ma_khach_hang = self.khach_hang.ma_khach_hang
        else:
            # Tạo mã khách hàng mới
            ma_khach_hang = f"KH{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'ma_khach_hang': ma_khach_hang,
            'ho_ten': self.ho_ten_input.text(),
            'dia_chi': self.dia_chi_input.text(),
            'so_dien_thoai': self.so_dien_thoai_input.text(),
            'ma_cong_to': self.ma_cong_to_input.text()
        }

class KhachHangTab(QWidget):
    """
    Tab quản lý khách hàng
    """
    
    def __init__(self, db):
        """
        Khởi tạo tab khách hàng
        
        Args:
            db (DatabaseHandler): Đối tượng xử lý dữ liệu
        """
        super().__init__()
        
        self.db = db
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Khởi tạo giao diện tab"""
        # Layout chính
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {VTN_YELLOW}; border-radius: 8px;")
        header_layout = QHBoxLayout(header_frame)
        
        header_label = QLabel("QUẢN LÝ KHÁCH HÀNG")
        header_label.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Panel tìm kiếm
        search_frame = QFrame()
        search_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 8px;")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 12, 15, 12)
        
        # Tìm kiếm
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã KH, tên khách hàng hoặc SĐT...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 6px;
                padding: 10px 12px;
                background-color: {VTN_DARK_BG};
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QLineEdit::placeholder {{
                color: #888888;
            }}
        """)
        
        self.search_button = QPushButton("Tìm kiếm")
        self.search_button.setIcon(QIcon("../assets/icons/search.svg"))
        self.search_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {VTN_YELLOW};
                color: {VTN_DARK_BG};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {VTN_YELLOW_HOVER};
            }}
        """)
        self.search_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        
        layout.addWidget(search_frame)
        
        # Panel chức năng
        tools_frame = QFrame()
        tools_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 8px;")
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(15, 12, 15, 12)
        
        # Tiêu đề panel
        tools_label = QLabel("Thao tác:")
        tools_label.setFont(QFont("Roboto Medium", 10, QFont.Weight.Bold))
        tools_label.setStyleSheet(f"color: {VTN_LIGHT_TEXT};")
        tools_layout.addWidget(tools_label)
        
        # Các nút chức năng
        self.add_button = QPushButton("Thêm mới")
        self.add_button.setIcon(QIcon("../assets/icons/add.svg"))
        
        self.edit_button = QPushButton("Sửa")
        self.edit_button.setIcon(QIcon("../assets/icons/edit.svg"))
        
        self.delete_button = QPushButton("Xóa")
        self.delete_button.setIcon(QIcon("../assets/icons/delete.svg"))
        
        self.refresh_button = QPushButton("Làm mới")
        self.refresh_button.setIcon(QIcon("../assets/icons/refresh.svg"))
        
        for btn in [self.add_button, self.edit_button, self.refresh_button]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {VTN_YELLOW};
                    color: {VTN_DARK_BG};
                    border: none;
                    border-radius: 6px;
                    padding: 10px 15px;
                    font-weight: bold;
                    min-width: 110px;
                    font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {VTN_YELLOW_HOVER};
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {VTN_RED};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                min-width: 110px;
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {VTN_RED_HOVER};
            }}
        """)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        tools_layout.addStretch()
        tools_layout.addWidget(self.add_button)
        tools_layout.addWidget(self.edit_button)
        tools_layout.addWidget(self.delete_button)
        tools_layout.addWidget(self.refresh_button)
        
        layout.addWidget(tools_frame)
        
        # Bảng hiển thị danh sách khách hàng
        table_frame = QFrame()
        table_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 8px;")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QLabel("Danh sách khách hàng")
        table_header.setFont(QFont("Roboto Medium", 11, QFont.Weight.Bold))
        table_header.setStyleSheet(f"color: {VTN_ORANGE}; padding: 5px;")
        table_layout.addWidget(table_header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Mã KH", "Họ tên", "Địa chỉ", "Số điện thoại", "Mã công tơ"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 8px;
                background-color: {VTN_DARK_BG};
                gridline-color: {VTN_GRAY_BORDER};
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QTableWidget::item:selected {{
                background-color: {VTN_YELLOW};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {VTN_DARKER_BG};
                color: {VTN_YELLOW};
                padding: 8px;
                border: 1px solid {VTN_GRAY_BORDER};
                font-weight: bold;
                font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
            }}
        """)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame, 1)  # 1 là stretch factor
        
        # Kết nối các sự kiện
        self.add_button.clicked.connect(self.add_khach_hang)
        self.edit_button.clicked.connect(self.edit_khach_hang)
        self.delete_button.clicked.connect(self.delete_khach_hang)
        self.refresh_button.clicked.connect(self.load_data)
        self.search_button.clicked.connect(self.search_khach_hang)
        self.search_input.returnPressed.connect(self.search_button.click)
    
    def load_data(self):
        """Tải dữ liệu khách hàng vào bảng"""
        try:
            # Lấy danh sách khách hàng
            khach_hang_list = self.db.get_all_khach_hang()
            
            # Xóa dữ liệu cũ
            self.table.setRowCount(0)
            
            # Thêm dữ liệu mới
            for row, kh in enumerate(khach_hang_list):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(kh.ma_khach_hang))
                self.table.setItem(row, 1, QTableWidgetItem(kh.ho_ten))
                self.table.setItem(row, 2, QTableWidgetItem(kh.dia_chi))
                self.table.setItem(row, 3, QTableWidgetItem(kh.so_dien_thoai))
                self.table.setItem(row, 4, QTableWidgetItem(kh.ma_cong_to))
                
                # Căn chỉnh: mã khách hàng và số điện thoại căn giữa
                self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.item(row, 3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.item(row, 4).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Xóa nội dung ô tìm kiếm
            self.search_input.clear()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu khách hàng: {str(e)}")
    
    def add_khach_hang(self):
        """Thêm khách hàng mới"""
        dialog = KhachHangDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Lấy dữ liệu từ dialog
            khach_hang_data = dialog.get_khach_hang_data()
            
            # Tạo đối tượng khách hàng
            khach_hang = KhachHang(
                khach_hang_data['ma_khach_hang'],
                khach_hang_data['ho_ten'],
                khach_hang_data['dia_chi'],
                khach_hang_data['so_dien_thoai'],
                khach_hang_data['ma_cong_to']
            )
            
            # Thêm vào database
            if self.db.add_khach_hang(khach_hang):
                QMessageBox.information(self, "Thông báo", "Thêm khách hàng thành công!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm khách hàng!")
    
    def edit_khach_hang(self):
        """Sửa thông tin khách hàng"""
        # Kiểm tra đã chọn dòng nào chưa
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần sửa!")
            return
        
        # Lấy dòng đầu tiên được chọn
        row = selected_rows[0].row()
        
        # Lấy mã khách hàng
        ma_khach_hang = self.table.item(row, 0).text()
        
        # Lấy thông tin khách hàng
        khach_hang = self.db.get_khach_hang(ma_khach_hang)
        
        if not khach_hang:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin khách hàng!")
            return
        
        # Hiển thị dialog sửa
        dialog = KhachHangDialog(self, khach_hang)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Lấy dữ liệu từ dialog
            khach_hang_data = dialog.get_khach_hang_data()
            
            # Cập nhật đối tượng khách hàng
            khach_hang = KhachHang(
                khach_hang_data['ma_khach_hang'],
                khach_hang_data['ho_ten'],
                khach_hang_data['dia_chi'],
                khach_hang_data['so_dien_thoai'],
                khach_hang_data['ma_cong_to']
            )
            
            # Cập nhật vào database
            if self.db.update_khach_hang(khach_hang):
                QMessageBox.information(self, "Thông báo", "Cập nhật thông tin khách hàng thành công!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể cập nhật thông tin khách hàng!")
    
    def delete_khach_hang(self):
        """Xóa khách hàng"""
        # Kiểm tra đã chọn dòng nào chưa
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn khách hàng cần xóa!")
            return
        
        # Lấy dòng đầu tiên được chọn
        row = selected_rows[0].row()
        
        # Lấy mã khách hàng và tên
        ma_khach_hang = self.table.item(row, 0).text()
        ten_khach_hang = self.table.item(row, 1).text()
        
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa", 
            f"Bạn có chắc chắn muốn xóa khách hàng {ten_khach_hang}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Thực hiện xóa
            if self.db.delete_khach_hang(ma_khach_hang):
                QMessageBox.information(self, "Thông báo", "Xóa khách hàng thành công!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa khách hàng!")
    
    def search_khach_hang(self):
        """Tìm kiếm khách hàng"""
        keyword = self.search_input.text().strip()
        
        if not keyword:
            self.load_data()
            return
        
        # Tìm kiếm
        khach_hang_list = self.db.search_khach_hang(keyword)
        
        # Xóa dữ liệu cũ
        self.table.setRowCount(0)
        
        # Thêm dữ liệu mới
        for row, kh in enumerate(khach_hang_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(kh.ma_khach_hang))
            self.table.setItem(row, 1, QTableWidgetItem(kh.ho_ten))
            self.table.setItem(row, 2, QTableWidgetItem(kh.dia_chi))
            self.table.setItem(row, 3, QTableWidgetItem(kh.so_dien_thoai))
            self.table.setItem(row, 4, QTableWidgetItem(kh.ma_cong_to)) 
            
            # Căn chỉnh: mã khách hàng và số điện thoại căn giữa
            self.table.item(row, 0).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.item(row, 3).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.item(row, 4).setTextAlignment(Qt.AlignmentFlag.AlignCenter) 