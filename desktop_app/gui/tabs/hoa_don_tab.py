#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
                           QFormLayout, QDialog, QMessageBox, QHeaderView,
                           QComboBox, QDateEdit, QSpinBox, QCheckBox, QFrame,
                           QGroupBox, QSizePolicy)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QColor

import datetime
from models.hoa_don import HoaDon

# Định nghĩa các màu chủ đạo theo logo VTN
VTN_YELLOW = "#FFB300"  # Màu vàng chính
VTN_ORANGE = "#FF9800"  # Màu cam
VTN_BACKGROUND = "#FFFDE7"  # Màu nền nhạt
VTN_TEXT = "#212121"  # Màu chữ

class HoaDonDialog(QDialog):
    """
    Dialog để thêm/sửa thông tin hóa đơn
    """
    
    def __init__(self, parent=None, db=None, hoa_don=None):
        """
        Khởi tạo dialog
        
        Args:
            parent (QWidget): Widget cha
            db (DatabaseHandler): Đối tượng xử lý dữ liệu
            hoa_don (HoaDon): Đối tượng hóa đơn (None nếu thêm mới)
        """
        super().__init__(parent)
        
        self.db = db
        self.hoa_don = hoa_don
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện dialog"""
        # Thiết lập cửa sổ
        title = "Thêm Hóa Đơn Mới" if not self.hoa_don else "Sửa Thông Tin Hóa Đơn"
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {VTN_BACKGROUND};
                border-radius: 8px;
            }}
            QLabel {{
                font-weight: bold;
                color: {VTN_TEXT};
            }}
            QLineEdit, QComboBox, QSpinBox, QDateEdit {{
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }}
            QPushButton {{
                background-color: {VTN_YELLOW};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {VTN_ORANGE};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {VTN_ORANGE};
            }}
        """)
        
        # Layout chính
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {VTN_YELLOW}; border-radius: 6px;")
        header_layout = QHBoxLayout(header_frame)
        
        header_label = QLabel(title)
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Form chính
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: white; border-radius: 6px; padding: 10px;")
        form_layout = QVBoxLayout(form_frame)
        
        # Thông tin cơ bản
        basic_group = QGroupBox("Thông tin cơ bản")
        basic_form = QFormLayout(basic_group)
        basic_form.setSpacing(10)
        
        # Chọn khách hàng
        self.khach_hang_combo = QComboBox()
        self.khach_hang_combo.setStyleSheet("padding: 5px;")
        self.load_khach_hang()
        
        # Thời gian
        date_frame = QFrame()
        date_layout = QHBoxLayout(date_frame)
        date_layout.setContentsMargins(0, 0, 0, 0)
        
        # Chọn tháng năm
        current_date = QDate.currentDate()
        
        self.thang_spin = QSpinBox()
        self.thang_spin.setRange(1, 12)
        self.thang_spin.setValue(current_date.month())
        
        self.nam_spin = QSpinBox()
        self.nam_spin.setRange(2000, 2100)
        self.nam_spin.setValue(current_date.year())
        
        date_layout.addWidget(self.thang_spin)
        date_layout.addWidget(QLabel("/"))
        date_layout.addWidget(self.nam_spin)
        
        basic_form.addRow("Khách hàng:", self.khach_hang_combo)
        basic_form.addRow("Kỳ thanh toán (Tháng/Năm):", date_frame)
        
        form_layout.addWidget(basic_group)
        
        # Thông tin chỉ số
        reading_group = QGroupBox("Chỉ số công tơ")
        reading_form = QFormLayout(reading_group)
        reading_form.setSpacing(10)
        
        # Chỉ số công tơ
        self.chi_so_dau_spin = QSpinBox()
        self.chi_so_dau_spin.setRange(0, 999999)
        
        self.chi_so_cuoi_spin = QSpinBox()
        self.chi_so_cuoi_spin.setRange(0, 999999)
        
        reading_form.addRow("Chỉ số đầu:", self.chi_so_dau_spin)
        reading_form.addRow("Chỉ số cuối:", self.chi_so_cuoi_spin)
        
        # Thông tin tiêu thụ
        self.tieu_thu_label = QLabel("Lượng điện tiêu thụ: 0 kWh")
        self.tieu_thu_label.setStyleSheet(f"color: {VTN_ORANGE}; font-size: 14px; padding: 5px; font-weight: bold;")
        reading_form.addRow("", self.tieu_thu_label)
        
        form_layout.addWidget(reading_group)
        
        # Thông tin thanh toán
        payment_group = QGroupBox("Thông tin thanh toán")
        payment_form = QFormLayout(payment_group)
        payment_form.setSpacing(10)
        
        # Trạng thái thanh toán
        payment_frame = QFrame()
        payment_layout = QHBoxLayout(payment_frame)
        payment_layout.setContentsMargins(0, 0, 0, 0)
        
        self.da_thanh_toan_check = QCheckBox("Đã thanh toán")
        self.da_thanh_toan_check.setStyleSheet("font-weight: bold;")
        payment_layout.addWidget(self.da_thanh_toan_check)
        
        # Ngày thanh toán
        date_label = QLabel("Ngày thanh toán:")
        date_label.setStyleSheet("margin-left: 20px;")
        payment_layout.addWidget(date_label)
        
        self.ngay_thanh_toan_date = QDateEdit()
        self.ngay_thanh_toan_date.setDate(current_date)
        self.ngay_thanh_toan_date.setEnabled(False)
        self.ngay_thanh_toan_date.setCalendarPopup(True)
        payment_layout.addWidget(self.ngay_thanh_toan_date)
        
        payment_form.addRow("", payment_frame)
        
        form_layout.addWidget(payment_group)
        
        # Kết nối sự kiện khi checkbox thay đổi
        self.da_thanh_toan_check.stateChanged.connect(self.on_thanh_toan_changed)
        
        # Kết nối sự kiện khi thay đổi chỉ số để cập nhật lượng tiêu thụ
        self.chi_so_dau_spin.valueChanged.connect(self.update_tieu_thu)
        self.chi_so_cuoi_spin.valueChanged.connect(self.update_tieu_thu)
        
        # Thêm form vào layout chính
        layout.addWidget(form_frame)
        
        # Nếu đang sửa thông tin, điền dữ liệu vào các trường
        if self.hoa_don:
            # Tìm index của khách hàng trong combo box
            index = self.khach_hang_combo.findData(self.hoa_don.ma_khach_hang)
            if index >= 0:
                self.khach_hang_combo.setCurrentIndex(index)
            
            self.thang_spin.setValue(self.hoa_don.thang)
            self.nam_spin.setValue(self.hoa_don.nam)
            self.chi_so_dau_spin.setValue(self.hoa_don.chi_so_dau)
            self.chi_so_cuoi_spin.setValue(self.hoa_don.chi_so_cuoi)
            self.da_thanh_toan_check.setChecked(self.hoa_don.da_thanh_toan)
            
            if self.hoa_don.ngay_thanh_toan:
                qdate = QDate(self.hoa_don.ngay_thanh_toan.year, 
                              self.hoa_don.ngay_thanh_toan.month,
                              self.hoa_don.ngay_thanh_toan.day)
                self.ngay_thanh_toan_date.setDate(qdate)
            
            self.update_tieu_thu()
        
        # Các nút
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.save_button = QPushButton("Lưu")
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setStyleSheet(f"""
            background-color: #f0f0f0; 
            color: {VTN_TEXT};
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Kết nối các sự kiện
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    def load_khach_hang(self):
        """Tải danh sách khách hàng vào combo box"""
        self.khach_hang_combo.clear()
        
        for kh in self.db.get_all_khach_hang():
            self.khach_hang_combo.addItem(f"{kh.ho_ten} ({kh.ma_khach_hang})", kh.ma_khach_hang)
    
    def on_thanh_toan_changed(self, state):
        """
        Xử lý sự kiện khi thay đổi trạng thái thanh toán
        
        Args:
            state (int): Trạng thái checkbox
        """
        self.ngay_thanh_toan_date.setEnabled(state == Qt.CheckState.Checked.value)
    
    def update_tieu_thu(self):
        """Cập nhật hiển thị lượng điện tiêu thụ"""
        chi_so_dau = self.chi_so_dau_spin.value()
        chi_so_cuoi = self.chi_so_cuoi_spin.value()
        
        tieu_thu = max(0, chi_so_cuoi - chi_so_dau)
        self.tieu_thu_label.setText(f"Lượng điện tiêu thụ: {tieu_thu} kWh")
    
    def get_hoa_don_data(self):
        """
        Lấy dữ liệu hóa đơn từ form
        
        Returns:
            dict: Dữ liệu hóa đơn
        """
        if self.hoa_don:
            ma_hoa_don = self.hoa_don.ma_hoa_don
        else:
            # Tạo mã hóa đơn mới
            ma_hoa_don = f"HD{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        ngay_thanh_toan = None
        if self.da_thanh_toan_check.isChecked():
            selected_date = self.ngay_thanh_toan_date.date()
            ngay_thanh_toan = datetime.datetime(
                selected_date.year(),
                selected_date.month(),
                selected_date.day()
            )
        
        return {
            'ma_hoa_don': ma_hoa_don,
            'ma_khach_hang': self.khach_hang_combo.currentData(),
            'thang': self.thang_spin.value(),
            'nam': self.nam_spin.value(),
            'chi_so_dau': self.chi_so_dau_spin.value(),
            'chi_so_cuoi': self.chi_so_cuoi_spin.value(),
            'da_thanh_toan': self.da_thanh_toan_check.isChecked(),
            'ngay_thanh_toan': ngay_thanh_toan,
            'so_tien': None  # Sẽ được tính toán sau
        }

class HoaDonTab(QWidget):
    """
    Tab quản lý hóa đơn
    """
    
    def __init__(self, db):
        """
        Khởi tạo tab hóa đơn
        
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
        header_frame.setStyleSheet(f"background-color: {VTN_YELLOW}; border-radius: 6px;")
        header_layout = QHBoxLayout(header_frame)
        
        header_label = QLabel("QUẢN LÝ HÓA ĐƠN TIỀN ĐIỆN")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Panel tìm kiếm và lọc
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: white; border-radius: 6px;")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 10, 15, 10)
        
        # Tìm kiếm
        search_label = QLabel("Tìm kiếm:")
        search_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nhập mã hóa đơn hoặc tên khách hàng...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: #f9f9f9;
            }
        """)
        
        self.search_button = QPushButton("Tìm")
        self.search_button.setIcon(QIcon.fromTheme("search"))
        self.search_button.setStyleSheet(f"""
            background-color: {VTN_YELLOW};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 15px;
            font-weight: bold;
        """)
        
        # Bộ lọc
        filter_label = QLabel("Lọc:")
        filter_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        self.thang_combo = QComboBox()
        self.thang_combo.addItem("Tất cả các tháng", 0)
        for i in range(1, 13):
            self.thang_combo.addItem(f"Tháng {i}", i)
        
        self.nam_combo = QComboBox()
        current_year = datetime.datetime.now().year
        self.nam_combo.addItem("Tất cả các năm", 0)
        for year in range(current_year - 5, current_year + 6):
            self.nam_combo.addItem(f"Năm {year}", year)
        
        self.thanh_toan_combo = QComboBox()
        self.thanh_toan_combo.addItem("Tất cả", -1)
        self.thanh_toan_combo.addItem("Đã thanh toán", 1)
        self.thanh_toan_combo.addItem("Chưa thanh toán", 0)
        
        self.filter_button = QPushButton("Áp dụng")
        self.filter_button.setIcon(QIcon.fromTheme("filter"))
        self.filter_button.setStyleSheet(f"""
            background-color: {VTN_ORANGE};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 15px;
            font-weight: bold;
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        search_layout.addSpacing(20)
        search_layout.addWidget(filter_label)
        search_layout.addWidget(self.thang_combo)
        search_layout.addWidget(self.nam_combo)
        search_layout.addWidget(self.thanh_toan_combo)
        search_layout.addWidget(self.filter_button)
        
        layout.addWidget(search_frame)
        
        # Panel chức năng
        tools_frame = QFrame()
        tools_frame.setStyleSheet("background-color: white; border-radius: 6px;")
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(15, 10, 15, 10)
        
        # Tiêu đề panel
        tools_label = QLabel("Thao tác:")
        tools_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        tools_layout.addWidget(tools_label)
        
        # Các nút chức năng
        self.add_button = QPushButton("Thêm hóa đơn")
        self.add_button.setIcon(QIcon.fromTheme("add"))
        
        self.edit_button = QPushButton("Sửa")
        self.edit_button.setIcon(QIcon.fromTheme("edit"))
        
        self.delete_button = QPushButton("Xóa")
        self.delete_button.setIcon(QIcon.fromTheme("delete"))
        
        self.print_button = QPushButton("In hóa đơn")
        self.print_button.setIcon(QIcon.fromTheme("print"))
        
        self.refresh_button = QPushButton("Làm mới")
        self.refresh_button.setIcon(QIcon.fromTheme("refresh"))
        
        for btn in [self.add_button, self.edit_button, self.print_button, self.refresh_button]:
            btn.setStyleSheet(f"""
                background-color: {VTN_YELLOW};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.delete_button.setStyleSheet(f"""
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 15px;
            font-weight: bold;
        """)
        
        tools_layout.addStretch()
        tools_layout.addWidget(self.add_button)
        tools_layout.addWidget(self.edit_button)
        tools_layout.addWidget(self.delete_button)
        tools_layout.addWidget(self.print_button)
        tools_layout.addWidget(self.refresh_button)
        
        layout.addWidget(tools_frame)
        
        # Bảng hiển thị danh sách hóa đơn
        table_frame = QFrame()
        table_frame.setStyleSheet("background-color: white; border-radius: 6px;")
        table_layout = QVBoxLayout(table_frame)
        
        table_header = QLabel("Danh sách hóa đơn")
        table_header.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        table_header.setStyleSheet(f"color: {VTN_ORANGE}; padding: 5px;")
        table_layout.addWidget(table_header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã hóa đơn", "Khách hàng", "Tháng/Năm", 
            "Chỉ số đầu", "Chỉ số cuối", "Tiêu thụ (kWh)", 
            "Thành tiền (đ)", "Trạng thái"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #FFB300;
                color: white;
            }
        """)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_frame, 1)  # 1 là stretch factor
        
        # Kết nối các sự kiện
        self.add_button.clicked.connect(self.add_hoa_don)
        self.edit_button.clicked.connect(self.edit_hoa_don)
        self.delete_button.clicked.connect(self.delete_hoa_don)
        self.refresh_button.clicked.connect(self.load_data)
        self.search_button.clicked.connect(self.search_hoa_don)
        self.filter_button.clicked.connect(self.apply_filter)
        self.search_input.returnPressed.connect(self.search_button.click)
        self.print_button.clicked.connect(self.print_hoa_don)
    
    def load_data(self):
        """Tải dữ liệu hóa đơn vào bảng"""
        # Lấy danh sách hóa đơn
        hoa_don_list = self.db.get_all_hoa_don()
        
        # Xóa dữ liệu cũ
        self.table.setRowCount(0)
        
        # Thêm dữ liệu từ database
        for row, hoa_don in enumerate(hoa_don_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(hoa_don.ma_hoa_don))  # Mã HĐ
            
            # Lấy thông tin khách hàng
            khach_hang = self.db.get_khach_hang(hoa_don.ma_khach_hang)
            ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không xác định"
            self.table.setItem(row, 1, QTableWidgetItem(ten_khach_hang))  # Tên KH
            
            self.table.setItem(row, 2, QTableWidgetItem(f"{hoa_don.thang}/{hoa_don.nam}"))  # Tháng/Năm
            self.table.setItem(row, 3, QTableWidgetItem(str(hoa_don.chi_so_dau)))  # Chỉ số đầu
            self.table.setItem(row, 4, QTableWidgetItem(str(hoa_don.chi_so_cuoi)))  # Chỉ số cuối
            
            # Tính lượng tiêu thụ
            tieu_thu = hoa_don.chi_so_cuoi - hoa_don.chi_so_dau
            self.table.setItem(row, 5, QTableWidgetItem(str(tieu_thu)))  # Tiêu thụ
            
            # Định dạng số tiền (hiển thị số nguyên, không có phần thập phân)
            so_tien = f"{int(hoa_don.so_tien):,} VNĐ" if hoa_don.so_tien else "Chưa tính"
            self.table.setItem(row, 6, QTableWidgetItem(so_tien))  # Số tiền
            
            # Trạng thái
            trang_thai = "Đã thanh toán" if hoa_don.da_thanh_toan else "Chưa thanh toán"
            trang_thai_item = QTableWidgetItem(trang_thai)
            trang_thai_item.setForeground(Qt.GlobalColor.darkGreen if hoa_don.da_thanh_toan else Qt.GlobalColor.darkRed)
            self.table.setItem(row, 7, trang_thai_item)
    
    def add_hoa_don(self):
        """Thêm hóa đơn mới"""
        dialog = HoaDonDialog(self, self.db)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Lấy dữ liệu từ dialog
            hoa_don_data = dialog.get_hoa_don_data()
            
            # Tạo đối tượng hóa đơn
            hoa_don = HoaDon(
                hoa_don_data['ma_hoa_don'],
                hoa_don_data['ma_khach_hang'],
                hoa_don_data['thang'],
                hoa_don_data['nam'],
                hoa_don_data['chi_so_dau'],
                hoa_don_data['chi_so_cuoi'],
                hoa_don_data['da_thanh_toan'],
                hoa_don_data['ngay_thanh_toan'],
                None
            )
            
            # Tính tiền
            bang_gia = self.db.get_bang_gia_hien_hanh()
            if bang_gia:
                hoa_don.tinh_tien(bang_gia)
            
            # Thêm vào database
            if self.db.add_hoa_don(hoa_don):
                QMessageBox.information(self, "Thông báo", "Thêm hóa đơn thành công!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm hóa đơn! Có thể đã tồn tại hóa đơn cho khách hàng này trong tháng đã chọn.")
    
    def edit_hoa_don(self):
        """Sửa thông tin hóa đơn"""
        # Kiểm tra đã chọn dòng nào chưa
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn hóa đơn cần sửa!")
            return
        
        # Lấy dòng đầu tiên được chọn
        row = selected_rows[0].row()
        
        # Lấy mã hóa đơn
        ma_hoa_don = self.table.item(row, 0).text()
        
        # Lấy thông tin hóa đơn
        hoa_don = self.db.get_hoa_don(ma_hoa_don)
        
        if not hoa_don:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin hóa đơn!")
            return
        
        # Hiển thị dialog sửa
        dialog = HoaDonDialog(self, self.db, hoa_don)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Lấy dữ liệu từ dialog
            hoa_don_data = dialog.get_hoa_don_data()
            
            # Cập nhật đối tượng hóa đơn
            hoa_don = HoaDon(
                hoa_don_data['ma_hoa_don'],
                hoa_don_data['ma_khach_hang'],
                hoa_don_data['thang'],
                hoa_don_data['nam'],
                hoa_don_data['chi_so_dau'],
                hoa_don_data['chi_so_cuoi'],
                hoa_don_data['da_thanh_toan'],
                hoa_don_data['ngay_thanh_toan'],
                hoa_don.so_tien
            )
            
            # Tính tiền nếu cần
            if hoa_don_data['chi_so_dau'] != self.table.item(row, 3).text() or hoa_don_data['chi_so_cuoi'] != self.table.item(row, 4).text():
                bang_gia = self.db.get_bang_gia_hien_hanh()
                if bang_gia:
                    hoa_don.tinh_tien(bang_gia)
            
            # Cập nhật vào database
            if self.db.update_hoa_don(hoa_don):
                QMessageBox.information(self, "Thông báo", "Cập nhật thông tin hóa đơn thành công!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể cập nhật thông tin hóa đơn!")
    
    def delete_hoa_don(self):
        """Xóa hóa đơn"""
        # Kiểm tra đã chọn dòng nào chưa
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn hóa đơn cần xóa!")
            return
        
        # Lấy dòng đầu tiên được chọn
        row = selected_rows[0].row()
        
        # Lấy mã hóa đơn và tên khách hàng
        ma_hoa_don = self.table.item(row, 0).text()
        ten_khach_hang = self.table.item(row, 1).text()
        thang_nam = self.table.item(row, 2).text()
        
        # Hiển thị hộp thoại xác nhận
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa", 
            f"Bạn có chắc chắn muốn xóa hóa đơn của khách hàng {ten_khach_hang} tháng {thang_nam}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Thực hiện xóa
            if self.db.delete_hoa_don(ma_hoa_don):
                QMessageBox.information(self, "Thông báo", "Xóa hóa đơn thành công!")
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể xóa hóa đơn!")
    
    def search_hoa_don(self):
        """Tìm kiếm hóa đơn"""
        keyword = self.search_input.text().strip()
        
        if not keyword:
            self.load_data()
            return
        
        # Xử lý filter theo tháng và năm
        thang_index = self.thang_combo.currentIndex()
        nam_text = self.nam_combo.currentText()
        
        thang = None if thang_index == 0 else thang_index
        
        # Xử lý chuỗi nam_text để trích xuất số năm
        if nam_text == "Tất cả năm":
            nam = None
        else:
            # Trích xuất số năm từ chuỗi (ví dụ: "Nam 2021" -> 2021)
            import re
            nam_match = re.search(r'\d{4}', nam_text)
            nam = int(nam_match.group()) if nam_match else None
        
        # Tìm kiếm
        hoa_don_list = self.db.search_hoa_don(keyword, thang, nam)
        
        # Xóa dữ liệu cũ
        self.table.setRowCount(0)
        
        # Thêm dữ liệu mới
        for row, hoa_don in enumerate(hoa_don_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(hoa_don.ma_hoa_don))  # Mã HĐ
            
            # Lấy thông tin khách hàng
            khach_hang = self.db.get_khach_hang(hoa_don.ma_khach_hang)
            ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không xác định"
            self.table.setItem(row, 1, QTableWidgetItem(ten_khach_hang))  # Tên KH
            
            self.table.setItem(row, 2, QTableWidgetItem(f"{hoa_don.thang}/{hoa_don.nam}"))  # Tháng/Năm
            self.table.setItem(row, 3, QTableWidgetItem(str(hoa_don.chi_so_dau)))  # Chỉ số đầu
            self.table.setItem(row, 4, QTableWidgetItem(str(hoa_don.chi_so_cuoi)))  # Chỉ số cuối
            
            # Tính lượng tiêu thụ
            tieu_thu = hoa_don.chi_so_cuoi - hoa_don.chi_so_dau
            self.table.setItem(row, 5, QTableWidgetItem(str(tieu_thu)))  # Tiêu thụ
            
            # Định dạng số tiền (hiển thị số nguyên, không có phần thập phân)
            so_tien = f"{int(hoa_don.so_tien):,} VNĐ" if hoa_don.so_tien else "Chưa tính"
            self.table.setItem(row, 6, QTableWidgetItem(so_tien))  # Số tiền
            
            # Trạng thái
            trang_thai = "Đã thanh toán" if hoa_don.da_thanh_toan else "Chưa thanh toán"
            trang_thai_item = QTableWidgetItem(trang_thai)
            trang_thai_item.setForeground(Qt.GlobalColor.darkGreen if hoa_don.da_thanh_toan else Qt.GlobalColor.darkRed)
            self.table.setItem(row, 7, trang_thai_item)
    
    def apply_filter(self):
        """Áp dụng bộ lọc"""
        thang_index = self.thang_combo.currentIndex()
        nam_text = self.nam_combo.currentText()
        
        thang = None if thang_index == 0 else thang_index
        
        # Xử lý chuỗi nam_text để trích xuất số năm
        if nam_text == "Tất cả năm":
            nam = None
        else:
            # Trích xuất số năm từ chuỗi (ví dụ: "Nam 2021" -> 2021)
            import re
            nam_match = re.search(r'\d{4}', nam_text)
            nam = int(nam_match.group()) if nam_match else None
        
        # Lọc hóa đơn theo tháng và năm
        hoa_don_list = []
        all_hoa_don = self.db.get_all_hoa_don()
        
        # Áp dụng bộ lọc
        for hd in all_hoa_don:
            # Lọc theo tháng nếu có
            if thang and hd.thang != thang:
                continue
            
            # Lọc theo năm nếu có
            if nam and hd.nam != nam:
                continue
            
            # Nếu vượt qua các điều kiện lọc, thêm vào danh sách kết quả
            hoa_don_list.append(hd)
        
        # Xóa dữ liệu cũ
        self.table.setRowCount(0)
        
        # Thêm dữ liệu mới
        for row, hoa_don in enumerate(hoa_don_list):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(hoa_don.ma_hoa_don))  # Mã HĐ
            
            # Lấy thông tin khách hàng
            khach_hang = self.db.get_khach_hang(hoa_don.ma_khach_hang)
            ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không xác định"
            self.table.setItem(row, 1, QTableWidgetItem(ten_khach_hang))  # Tên KH
            
            self.table.setItem(row, 2, QTableWidgetItem(f"{hoa_don.thang}/{hoa_don.nam}"))  # Tháng/Năm
            self.table.setItem(row, 3, QTableWidgetItem(str(hoa_don.chi_so_dau)))  # Chỉ số đầu
            self.table.setItem(row, 4, QTableWidgetItem(str(hoa_don.chi_so_cuoi)))  # Chỉ số cuối
            
            # Tính lượng tiêu thụ
            tieu_thu = hoa_don.chi_so_cuoi - hoa_don.chi_so_dau
            self.table.setItem(row, 5, QTableWidgetItem(str(tieu_thu)))  # Tiêu thụ
            
            # Định dạng số tiền (hiển thị số nguyên, không có phần thập phân)
            so_tien = f"{int(hoa_don.so_tien):,} VNĐ" if hoa_don.so_tien else "Chưa tính"
            self.table.setItem(row, 6, QTableWidgetItem(so_tien))  # Số tiền
            
            # Trạng thái
            trang_thai = "Đã thanh toán" if hoa_don.da_thanh_toan else "Chưa thanh toán"
            trang_thai_item = QTableWidgetItem(trang_thai)
            trang_thai_item.setForeground(Qt.GlobalColor.darkGreen if hoa_don.da_thanh_toan else Qt.GlobalColor.darkRed)
            self.table.setItem(row, 7, trang_thai_item)
    
    def print_hoa_don(self):
        """In hóa đơn được chọn dưới dạng PDF"""
        # Kiểm tra xem có dòng nào được chọn không
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn hóa đơn cần in.")
            return
        
        # Lấy chỉ số dòng được chọn
        row_index = selected_rows[0].row()
        
        # Lấy mã hóa đơn từ dòng được chọn
        ma_hoa_don = self.table.item(row_index, 0).text()
        
        # Lấy thông tin hóa đơn
        hoa_don = self.db.get_hoa_don_by_id(ma_hoa_don)
        if not hoa_don:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy thông tin hóa đơn {ma_hoa_don}.")
            return
        
        # Lấy thông tin khách hàng
        khach_hang = self.db.get_khach_hang_by_id(hoa_don.ma_khach_hang)
        if not khach_hang:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy thông tin khách hàng của hóa đơn {ma_hoa_don}.")
            return
        
        # Lấy thông tin bảng giá
        bang_gia = self.db.get_bang_gia_by_date(hoa_don.thang, hoa_don.nam)
        if not bang_gia:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy thông tin bảng giá cho hóa đơn {ma_hoa_don}.")
            return
        
        try:
            # Import HoaDonPDF
            from models.hoa_don_pdf import HoaDonPDF
            
            # Tạo hóa đơn PDF
            hoa_don_pdf = HoaDonPDF()
            pdf_path = hoa_don_pdf.tao_hoa_don(hoa_don, khach_hang, bang_gia)
            
            # Hiển thị thông báo thành công
            QMessageBox.information(self, "Thành công", f"Đã xuất hóa đơn PDF thành công.\nVị trí: {pdf_path}")
            
            # Mở file PDF
            import os
            import platform
            import subprocess
            
            if platform.system() == 'Windows':
                os.startfile(pdf_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', pdf_path])
            else:  # Linux
                subprocess.run(['xdg-open', pdf_path])
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi tạo hóa đơn PDF: {str(e)}") 