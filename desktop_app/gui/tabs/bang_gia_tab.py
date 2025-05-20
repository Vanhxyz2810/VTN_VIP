#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
                           QFormLayout, QDialog, QMessageBox, QHeaderView,
                           QDateEdit, QDoubleSpinBox, QGroupBox, QScrollArea,
                           QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QColor

import datetime
from models.bang_gia import BangGia

# Định nghĩa các màu chủ đạo theo logo VTN
VTN_YELLOW = "#FFB300"  # Màu vàng chính
VTN_ORANGE = "#FF9800"  # Màu cam
VTN_BACKGROUND = "#FFFDE7"  # Màu nền nhạt
VTN_TEXT = "#212121"  # Màu chữ

class BangGiaDialog(QDialog):
    """
    Dialog để thêm/sửa bảng giá điện
    """
    
    def __init__(self, parent=None, bang_gia=None):
        """
        Khởi tạo dialog
        
        Args:
            parent (QWidget): Widget cha
            bang_gia (BangGia): Đối tượng bảng giá (None nếu thêm mới)
        """
        super().__init__(parent)
        
        self.bang_gia = bang_gia
        self.bac_thang_inputs = []
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện dialog"""
        # Thiết lập cửa sổ
        title = "Thêm Bảng Giá Mới" if not self.bang_gia else "Sửa Bảng Giá Điện"
        self.setWindowTitle(title)
        self.setMinimumWidth(550)
        self.setMinimumHeight(600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {VTN_BACKGROUND};
                border-radius: 8px;
            }}
            QLabel {{
                font-weight: bold;
                color: {VTN_TEXT};
            }}
            QDateEdit, QDoubleSpinBox {{
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
            QPushButton#deleteButton {{
                background-color: #f44336;
                padding: 5px 10px;
                min-width: 60px;
            }}
            QPushButton#addButton {{
                background-color: #4CAF50;
                padding: 8px 10px;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 20px;
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
        main_frame = QFrame()
        main_frame.setStyleSheet("background-color: white; border-radius: 6px; padding: 10px;")
        main_layout = QVBoxLayout(main_frame)
        
        # Form layout cho thông tin chung
        basic_group = QGroupBox("Thông tin cơ bản")
        form_layout = QFormLayout(basic_group)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 20, 15, 15)
        
        # Các trường nhập liệu cơ bản
        # Ngày áp dụng
        self.ngay_ap_dung_date = QDateEdit()
        self.ngay_ap_dung_date.setDate(QDate.currentDate())
        self.ngay_ap_dung_date.setCalendarPopup(True)
        
        # Thuế VAT
        self.vat_spin = QDoubleSpinBox()
        self.vat_spin.setRange(0, 1)
        self.vat_spin.setSingleStep(0.01)
        self.vat_spin.setValue(0.1)  # 10% mặc định
        self.vat_spin.setDecimals(2)
        self.vat_spin.setSuffix(" (10%)")
        
        # Thêm các trường vào form
        form_layout.addRow(QLabel("Ngày áp dụng:"), self.ngay_ap_dung_date)
        form_layout.addRow(QLabel("Thuế VAT:"), self.vat_spin)
        
        # Thêm form vào layout chính
        main_layout.addWidget(basic_group)
        
        # Tạo khu vực cuộn cho các bậc thang giá
        bac_thang_group = QGroupBox("Bảng Giá Điện Theo Bậc Thang")
        bac_thang_layout = QVBoxLayout(bac_thang_group)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #FFB300;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        bac_thang_container = QWidget()
        self.bac_thang_layout = QVBoxLayout(bac_thang_container)
        self.bac_thang_layout.setSpacing(10)
        
        # Tiêu đề
        bac_thang_title = QLabel("Cấu hình các mức giá theo lượng điện tiêu thụ")
        bac_thang_title.setFont(QFont("Arial", 10))
        bac_thang_title.setStyleSheet(f"color: {VTN_TEXT}; font-weight: normal;")
        bac_thang_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.bac_thang_layout.addWidget(bac_thang_title)
        
        # Nếu có bảng giá sẵn, hiển thị dữ liệu
        if self.bang_gia:
            for i, (kwh_max, don_gia) in enumerate(self.bang_gia.bac_thang):
                self.add_bac_thang_ui(i+1, kwh_max, don_gia)
        else:
            # Thêm bậc thang mặc định của EVN
            default_bac_thang = [
                (50, 1728),     # Bậc 1: 0-50 kWh
                (100, 1786),    # Bậc 2: 51-100 kWh
                (200, 2074),    # Bậc 3: 101-200 kWh
                (300, 2612),    # Bậc 4: 201-300 kWh
                (400, 2919),    # Bậc 5: 301-400 kWh
                (float('inf'), 3015)  # Bậc 6: Trên 400 kWh
            ]
            
            for i, (kwh_max, don_gia) in enumerate(default_bac_thang):
                self.add_bac_thang_ui(i+1, kwh_max, don_gia)
        
        # Nút thêm bậc thang mới
        add_bac_button = QPushButton("+ Thêm bậc thang mới")
        add_bac_button.setObjectName("addButton")
        add_bac_button.setIcon(QIcon.fromTheme("add"))
        add_bac_button.clicked.connect(self.on_add_bac_thang)
        self.bac_thang_layout.addWidget(add_bac_button)
        
        scroll_area.setWidget(bac_thang_container)
        bac_thang_layout.addWidget(scroll_area)
        
        main_layout.addWidget(bac_thang_group)
        layout.addWidget(main_frame)
        
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
    
    def add_bac_thang_ui(self, bac_so, kwh_max=100, don_gia=1000):
        """
        Thêm UI cho một bậc thang giá
        
        Args:
            bac_so (int): Số thứ tự bậc
            kwh_max (float): Giới hạn trên của bậc thang
            don_gia (float): Đơn giá cho bậc thang
        """
        # Tạo frame cho bậc thang
        bac_frame = QFrame()
        bac_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: {"#f9f9f9" if bac_so % 2 == 0 else "white"};
                padding: 5px;
            }}
        """)
        
        # Layout cho bậc thang
        bac_layout = QHBoxLayout(bac_frame)
        bac_layout.setContentsMargins(10, 10, 10, 10)
        
        # Tiêu đề bậc thang
        bac_label = QLabel(f"Bậc {bac_so}")
        bac_label.setStyleSheet(f"color: {VTN_ORANGE}; font-weight: bold;")
        bac_label.setFixedWidth(50)
        bac_layout.addWidget(bac_label)
        
        # Trường nhập kWh tối đa
        kwh_max_spin = QDoubleSpinBox()
        kwh_max_spin.setRange(1, 10000)
        kwh_max_spin.setValue(kwh_max)
        kwh_max_spin.setDecimals(0)
        kwh_max_spin.setSuffix(" kWh")
        kwh_max_spin.setMinimumWidth(150)
        
        # Đặc biệt cho bậc cao nhất
        if kwh_max == float('inf'):
            kwh_max_spin.setSpecialValueText("Không giới hạn")
            kwh_max_spin.setValue(10000)
            kwh_max_spin.setEnabled(False)
        
        # Trường nhập đơn giá
        don_gia_spin = QDoubleSpinBox()
        don_gia_spin.setRange(1, 100000)
        don_gia_spin.setValue(don_gia)
        don_gia_spin.setDecimals(0)
        don_gia_spin.setSuffix(" đ/kWh")
        don_gia_spin.setMinimumWidth(150)
        
        # Label phạm vi
        if bac_so == 1:
            range_label = QLabel("Từ 0 đến:")
        else:
            previous_limit = self.bac_thang_inputs[-1][0].value()
            range_label = QLabel(f"Từ {int(previous_limit) + 1} đến:")
        
        range_label.setFixedWidth(80)
        
        # Nút xóa bậc thang
        delete_button = QPushButton("Xóa")
        delete_button.setObjectName("deleteButton")
        delete_button.setIcon(QIcon.fromTheme("delete"))
        delete_button.clicked.connect(lambda: self.on_delete_bac_thang(bac_frame))
        delete_button.setFixedWidth(60)
        
        # Thêm các trường vào layout
        bac_layout.addWidget(range_label)
        bac_layout.addWidget(kwh_max_spin)
        bac_layout.addWidget(QLabel("Đơn giá:"))
        bac_layout.addWidget(don_gia_spin)
        bac_layout.addStretch()
        bac_layout.addWidget(delete_button)
        
        # Thêm vào layout chính
        self.bac_thang_layout.insertWidget(self.bac_thang_layout.count() - 1, bac_frame)
        
        # Lưu lại các trường nhập liệu
        self.bac_thang_inputs.append((kwh_max_spin, don_gia_spin, bac_frame))
    
    def on_add_bac_thang(self):
        """Xử lý sự kiện khi thêm bậc thang mới"""
        bac_so = len(self.bac_thang_inputs) + 1
        
        # Nếu đã có bậc thang, lấy giá trị kWh max của bậc cuối cùng
        default_kwh_max = 100
        if self.bac_thang_inputs:
            last_kwh_max = self.bac_thang_inputs[-1][0].value()
            default_kwh_max = last_kwh_max + 100
        
        self.add_bac_thang_ui(bac_so, default_kwh_max, 1000)
    
    def on_delete_bac_thang(self, frame):
        """
        Xử lý sự kiện khi xóa bậc thang
        
        Args:
            frame (QFrame): Frame cần xóa
        """
        if len(self.bac_thang_inputs) <= 1:
            QMessageBox.warning(self, "Cảnh báo", "Cần có ít nhất một bậc thang giá!")
            return
        
        # Tìm và xóa phần tử tương ứng
        for i, (_, _, box) in enumerate(self.bac_thang_inputs):
            if box == frame:
                self.bac_thang_inputs.pop(i)
                break
        
        # Xóa khỏi UI
        frame.deleteLater()
        
        # Cập nhật lại các label phạm vi
        for i, (kwh_spin, _, box) in enumerate(self.bac_thang_inputs):
            layout = box.layout()
            bac_label = layout.itemAt(0).widget()
            range_label = layout.itemAt(1).widget()
            
            # Cập nhật label bậc
            bac_label.setText(f"Bậc {i+1}")
            
            # Cập nhật label phạm vi
            if i == 0:
                range_label.setText("Từ 0 đến:")
            else:
                previous_limit = self.bac_thang_inputs[i-1][0].value()
                range_label.setText(f"Từ {int(previous_limit) + 1} đến:")
    
    def get_bang_gia_data(self):
        """
        Lấy dữ liệu bảng giá từ form
        
        Returns:
            dict: Dữ liệu bảng giá
        """
        if self.bang_gia:
            ma_bang_gia = self.bang_gia.ma_bang_gia
        else:
            # Tạo mã bảng giá mới
            ma_bang_gia = f"BG{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Lấy ngày áp dụng
        selected_date = self.ngay_ap_dung_date.date()
        ngay_ap_dung = datetime.datetime(
            selected_date.year(),
            selected_date.month(),
            selected_date.day()
        )
        
        # Lấy thông tin các bậc thang
        bac_thang = []
        for kwh_max_spin, don_gia_spin, _ in self.bac_thang_inputs:
            kwh_max = kwh_max_spin.value()
            
            # Kiểm tra nếu là bậc cuối cùng và đã bị vô hiệu hóa
            if not kwh_max_spin.isEnabled():
                kwh_max = float('inf')
                
            don_gia = don_gia_spin.value()
            bac_thang.append((kwh_max, don_gia))
        
        return {
            'ma_bang_gia': ma_bang_gia,
            'ngay_ap_dung': ngay_ap_dung,
            'bac_thang': bac_thang,
            'vat': self.vat_spin.value()
        }

class BangGiaTab(QWidget):
    """
    Tab quản lý bảng giá điện
    """
    
    def __init__(self, db):
        """
        Khởi tạo tab bảng giá
        
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
        
        header_label = QLabel("QUẢN LÝ BẢNG GIÁ ĐIỆN")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
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
        self.add_button = QPushButton("Thêm bảng giá mới")
        self.add_button.setIcon(QIcon.fromTheme("add"))
        
        self.history_button = QPushButton("Lịch sử bảng giá")
        self.history_button.setIcon(QIcon.fromTheme("history"))
        
        self.refresh_button = QPushButton("Làm mới")
        self.refresh_button.setIcon(QIcon.fromTheme("refresh"))
        
        for btn in [self.add_button, self.history_button, self.refresh_button]:
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
        
        tools_layout.addStretch()
        tools_layout.addWidget(self.add_button)
        tools_layout.addWidget(self.history_button)
        tools_layout.addWidget(self.refresh_button)
        
        layout.addWidget(tools_frame)
        
        # Khu vực hiển thị bảng giá
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: white; border-radius: 6px;")
        content_layout = QVBoxLayout(content_frame)
        
        self.current_price_label = QLabel("BẢNG GIÁ HIỆN TẠI")
        self.current_price_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.current_price_label.setStyleSheet(f"color: {VTN_ORANGE}; padding: 5px;")
        content_layout.addWidget(self.current_price_label)
        
        # Bảng hiển thị bảng giá hiện tại
        self.current_table = QTableWidget()
        self.current_table.setColumnCount(3)
        self.current_table.setHorizontalHeaderLabels(["Bậc thang", "Định mức (kWh)", "Đơn giá (đ/kWh)"])
        self.current_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.current_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.current_table.setAlternatingRowColors(True)
        self.current_table.setStyleSheet("""
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
        content_layout.addWidget(self.current_table)
        
        # Thông tin bảng giá hiện tại
        self.current_info_frame = QFrame()
        info_layout = QHBoxLayout(self.current_info_frame)
        
        self.current_date_label = QLabel("Ngày áp dụng: --/--/----")
        self.current_date_label.setStyleSheet("font-weight: bold;")
        
        self.current_vat_label = QLabel("Thuế VAT: 10%")
        self.current_vat_label.setStyleSheet("font-weight: bold;")
        
        info_layout.addWidget(self.current_date_label)
        info_layout.addStretch()
        info_layout.addWidget(self.current_vat_label)
        
        content_layout.addWidget(self.current_info_frame)
        
        # Bảng hiển thị lịch sử bảng giá
        self.history_label = QLabel("LỊCH SỬ BẢNG GIÁ")
        self.history_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.history_label.setStyleSheet(f"color: {VTN_ORANGE}; padding: 5px;")
        self.history_label.setVisible(False)
        content_layout.addWidget(self.history_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Mã bảng giá", "Ngày áp dụng", "Thuế VAT"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet("""
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
        self.history_table.setVisible(False)
        content_layout.addWidget(self.history_table)
        
        layout.addWidget(content_frame, 1)  # 1 là stretch factor
        
        # Kết nối các sự kiện
        self.add_button.clicked.connect(self.add_bang_gia)
        self.history_button.clicked.connect(self.toggle_history_view)
        self.refresh_button.clicked.connect(self.load_data)
    
    def load_data(self):
        """Tải dữ liệu bảng giá hiện hành"""
        self.load_current_bang_gia()
    
    def load_current_bang_gia(self):
        """Tải thông tin bảng giá hiện hành"""
        # Tạm thời dùng dữ liệu mẫu
        bang_gia = self.db.get_bang_gia_hien_hanh()
        
        if not bang_gia:
            # Hiển thị thông báo nếu chưa có bảng giá
            self.current_date_label.setText("Chưa có bảng giá nào. Vui lòng thêm bảng giá mới.")
            self.current_vat_label.setText("")
            return
            
        # Hiển thị thông tin bảng giá
        self.current_date_label.setText(f"Ngày áp dụng: {bang_gia.ngay_ap_dung.strftime('%d/%m/%Y')}")
        self.current_vat_label.setText(f"Thuế VAT: {bang_gia.vat * 100:.0f}%")
        
        # Cập nhật bảng giá bậc thang
        self.current_table.setRowCount(0)
        
        for i, (kwh_max, don_gia) in enumerate(bang_gia.bac_thang):
            self.current_table.insertRow(i)
            
            # Bậc thang
            self.current_table.setItem(i, 0, QTableWidgetItem(f"Bậc {i+1}"))
            
            # Khoảng kWh
            if i == 0:
                range_text = f"0 - {kwh_max}"
            else:
                prev_max = bang_gia.bac_thang[i-1][0]
                range_text = f"{prev_max + 1} - {'∞' if kwh_max == float('inf') else kwh_max}"
            
            self.current_table.setItem(i, 1, QTableWidgetItem(range_text))
            
            # Đơn giá
            self.current_table.setItem(i, 2, QTableWidgetItem(f"{don_gia:,}"))
    
    def load_bang_gia_history(self):
        """Tải lịch sử bảng giá"""
        # Lấy danh sách bảng giá
        bang_gia_list = self.db.get_all_bang_gia()
        
        # Cập nhật bảng lịch sử
        self.history_table.setRowCount(0)
        
        for i, bg in enumerate(bang_gia_list):
            self.history_table.insertRow(i)
            self.history_table.setItem(i, 0, QTableWidgetItem(bg.ma_bang_gia))
            self.history_table.setItem(i, 1, QTableWidgetItem(bg.ngay_ap_dung.strftime('%d/%m/%Y')))
            
            # Mô tả (số bậc thang và thuế VAT)
            mo_ta = f"Có {len(bg.bac_thang)} bậc thang, VAT {bg.vat * 100:.0f}%"
            self.history_table.setItem(i, 2, QTableWidgetItem(mo_ta))
    
    def add_bang_gia(self):
        """Thêm bảng giá mới"""
        dialog = BangGiaDialog(self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Lấy dữ liệu từ dialog
            bang_gia_data = dialog.get_bang_gia_data()
            
            # Tạo đối tượng bảng giá
            bang_gia = BangGia(
                bang_gia_data['ma_bang_gia'],
                bang_gia_data['ngay_ap_dung'],
                bang_gia_data['bac_thang']
            )
            bang_gia.vat = bang_gia_data['vat']
            
            # Thêm vào database
            if self.db.add_bang_gia(bang_gia):
                QMessageBox.information(
                    self, 
                    "Thông báo", 
                    f"Đã thêm bảng giá mới với ngày áp dụng: {bang_gia_data['ngay_ap_dung'].strftime('%d/%m/%Y')}"
                )
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể thêm bảng giá mới!")
            
            # Cập nhật giao diện
            self.load_current_bang_gia()
            if self.history_table.isVisible():
                self.load_bang_gia_history()
    
    def toggle_history_view(self):
        """Bật/tắt hiển thị lịch sử bảng giá"""
        # Thay đổi hiển thị của bảng lịch sử
        is_visible = self.history_table.isVisible()
        self.history_table.setVisible(not is_visible)
        self.history_label.setVisible(not is_visible)
        
        # Cập nhật nút
        if not is_visible:
            self.history_button.setText("Ẩn lịch sử bảng giá")
            self.load_bang_gia_history()
        else:
            self.history_button.setText("Xem lịch sử bảng giá") 