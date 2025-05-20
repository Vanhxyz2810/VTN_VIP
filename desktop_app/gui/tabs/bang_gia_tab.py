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
VTN_DARK_BG = "#121212"  # Màu nền tối
VTN_DARKER_BG = "#1E1E1E"  # Màu nền tối hơn cho các panel
VTN_LIGHT_TEXT = "#EEEEEE"  # Màu chữ sáng
VTN_ACCENT = "#FFC107"  # Màu nhấn
VTN_RED = "#D32F2F"  # Màu đỏ cho nút xóa
VTN_RED_HOVER = "#B71C1C"  # Màu đỏ đậm hơn khi hover
VTN_YELLOW_HOVER = "#FFA000"  # Màu vàng đậm hơn khi hover
VTN_GRAY_BORDER = "#555555"  # Màu viền xám đậm

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
        title = "Thêm Bảng Giá Điện Mới" if not self.bang_gia else "Sửa Bảng Giá Điện"
        self.setWindowTitle(title)
        self.setMinimumWidth(750)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {VTN_DARK_BG};
                border-radius: 8px;
            }}
            QLabel {{
                font-weight: bold;
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
            QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 4px;
                padding: 8px;
                background-color: {VTN_DARKER_BG};
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
            QPushButton {{
                background-color: {VTN_YELLOW};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {VTN_YELLOW_HOVER};
            }}
            QPushButton:disabled {{
                background-color: #555;
                color: #888;
            }}
            QScrollArea, QGroupBox {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 6px;
            }}
            QGroupBox {{
                margin-top: 12px;
                background-color: {VTN_DARKER_BG};
                font-family: 'Roboto', 'Arial', sans-serif;
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
        header_label.setFont(QFont("Roboto", 14, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Form chính
        main_frame = QFrame()
        main_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 6px; padding: 10px;")
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
        
        # Scroll area cho nhiều bậc thang
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"background-color: {VTN_DARKER_BG};")
        
        # Widget chứa các bậc thang
        self.bac_thang_widget = QWidget()
        self.bac_thang_widget.setStyleSheet(f"background-color: {VTN_DARKER_BG};")
        self.bac_thang_container = QVBoxLayout(self.bac_thang_widget)
        self.bac_thang_container.setContentsMargins(5, 5, 5, 5)
        self.bac_thang_container.setSpacing(10)
        
        # Thêm widget vào scroll area
        scroll_area.setWidget(self.bac_thang_widget)
        bac_thang_layout.addWidget(scroll_area)
        
        # Thêm nút thêm bậc thang mới
        add_button_layout = QHBoxLayout()
        self.add_bac_button = QPushButton("Thêm bậc thang")
        self.add_bac_button.setIcon(QIcon.fromTheme("add"))
        self.add_bac_button.clicked.connect(self.add_bac_thang)
        add_button_layout.addStretch()
        add_button_layout.addWidget(self.add_bac_button)
        bac_thang_layout.addLayout(add_button_layout)
        
        main_layout.addWidget(bac_thang_group)
        
        # Thêm main frame vào layout chính
        layout.addWidget(main_frame)
        
        # Các nút
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.save_button = QPushButton("Lưu")
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setStyleSheet(f"""
            background-color: #555; 
            color: {VTN_LIGHT_TEXT};
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Kết nối các sự kiện
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Nếu đang sửa thông tin, điền dữ liệu vào các trường
        if self.bang_gia:
            qdate = QDate(
                self.bang_gia.ngay_ap_dung.year,
                self.bang_gia.ngay_ap_dung.month,
                self.bang_gia.ngay_ap_dung.day
            )
            self.ngay_ap_dung_date.setDate(qdate)
            self.vat_spin.setValue(self.bang_gia.vat)
            
            # Thêm các bậc thang hiện tại
            for i, (kwh_max, don_gia) in enumerate(self.bang_gia.bac_thang):
                # Tạo UI cho bậc thang
                self.add_bac_thang()
                
                # Cập nhật giá trị
                bac_frame, kwh_spin, don_gia_spin, _ = self.bac_thang_inputs[i]
                kwh_spin.setValue(int(kwh_max) if kwh_max != float('inf') else 0)
                
                # Nếu là bậc cuối cùng và giá trị là vô cùng, vô hiệu hóa trường KWh
                if i == len(self.bang_gia.bac_thang) - 1 and kwh_max == float('inf'):
                    kwh_spin.setEnabled(False)
                
                don_gia_spin.setValue(don_gia)
        else:
            # Thêm 3 bậc thang mặc định
            for _ in range(3):
                self.add_bac_thang()
    
    def add_bac_thang(self):
        """Thêm một bậc thang mới vào form"""
        # Tạo frame cho một bậc
        bac_frame = QFrame()
        bac_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {VTN_DARKER_BG};
                border: 1px solid #555;
                border-radius: 6px;
                padding: 5px;
            }}
        """)
        
        bac_layout = QHBoxLayout(bac_frame)
        
        # Số thứ tự bậc thang
        bac_index = len(self.bac_thang_inputs) + 1
        bac_label = QLabel(f"Bậc {bac_index}:")
        bac_label.setStyleSheet("min-width: 60px;")
        
        # Khoảng kWh
        kwh_label = QLabel("Đến:")
        
        kwh_max_spin = QDoubleSpinBox()
        kwh_max_spin.setRange(1, 10000)
        kwh_max_spin.setValue(100 * bac_index)  # Giá trị mặc định
        kwh_max_spin.setSuffix(" kWh")
        kwh_max_spin.setDecimals(0)
        
        # Đơn giá
        don_gia_label = QLabel("Đơn giá:")
        
        don_gia_spin = QDoubleSpinBox()
        don_gia_spin.setRange(100, 10000)
        don_gia_spin.setValue(1500 + (bac_index - 1) * 200)  # Giá trị mặc định tăng dần theo bậc
        don_gia_spin.setSuffix(" đ/kWh")
        don_gia_spin.setDecimals(0)
        
        # Nút xóa
        delete_button = QPushButton("Xóa")
        delete_button.setIcon(QIcon.fromTheme("delete"))
        delete_button.setStyleSheet("""
            background-color: #f44336;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            min-width: 60px;
        """)
        
        # Kết nối sự kiện xóa
        delete_button.clicked.connect(lambda: self.remove_bac_thang(bac_frame))
        
        # Thêm các widget vào layout
        bac_layout.addWidget(bac_label)
        bac_layout.addWidget(kwh_label)
        bac_layout.addWidget(kwh_max_spin)
        bac_layout.addWidget(don_gia_label)
        bac_layout.addWidget(don_gia_spin)
        bac_layout.addWidget(delete_button)
        
        # Thêm vào container
        self.bac_thang_container.addWidget(bac_frame)
        
        # Lưu tham chiếu
        self.bac_thang_inputs.append((bac_frame, kwh_max_spin, don_gia_spin, delete_button))
        
        # Cập nhật trạng thái của nút xóa (nếu chỉ còn 1 bậc thì không cho xóa)
        self.update_delete_buttons()
    
    def remove_bac_thang(self, bac_frame):
        """Xóa một bậc thang khỏi form"""
        # Tìm index của bậc cần xóa
        for i, (frame, _, _, _) in enumerate(self.bac_thang_inputs):
            if frame == bac_frame:
                # Xóa khỏi layout và danh sách
                self.bac_thang_container.removeWidget(frame)
                frame.deleteLater()
                self.bac_thang_inputs.pop(i)
                break
        
        # Cập nhật lại các nhãn bậc
        for i, (_, _, _, _) in enumerate(self.bac_thang_inputs):
            # Tìm label bậc thang trong frame
            bac_label = self.bac_thang_inputs[i][0].layout().itemAt(0).widget()
            bac_label.setText(f"Bậc {i+1}:")
        
        # Cập nhật trạng thái của nút xóa
        self.update_delete_buttons()
    
    def update_delete_buttons(self):
        """Cập nhật trạng thái của các nút xóa"""
        # Nếu chỉ còn 1 bậc thì không cho xóa
        can_delete = len(self.bac_thang_inputs) > 1
        
        # Cập nhật trạng thái của tất cả các nút
        for _, _, _, delete_button in self.bac_thang_inputs:
            delete_button.setEnabled(can_delete)
    
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
        header_label.setFont(QFont("Roboto", 12, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Panel chức năng
        tools_frame = QFrame()
        tools_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 6px;")
        tools_layout = QHBoxLayout(tools_frame)
        tools_layout.setContentsMargins(15, 10, 15, 10)
        
        # Tiêu đề panel
        tools_label = QLabel("Thao tác:")
        tools_label.setFont(QFont("Roboto", 10, QFont.Weight.Bold))
        tools_label.setStyleSheet(f"color: {VTN_LIGHT_TEXT};")
        tools_layout.addWidget(tools_label)
        
        # Các nút chức năng
        self.add_button = QPushButton("Thêm bảng giá mới")
        self.add_button.setIcon(QIcon("../assets/icons/add.svg"))
        
        self.history_button = QPushButton("Lịch sử bảng giá")
        self.history_button.setIcon(QIcon("../assets/icons/history.svg"))
        
        self.refresh_button = QPushButton("Làm mới")
        self.refresh_button.setIcon(QIcon("../assets/icons/refresh.svg"))
        
        for btn in [self.add_button, self.history_button, self.refresh_button]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {VTN_YELLOW};
                    color: {VTN_DARK_BG};
                    border: none;
                    border-radius: 4px;
                    padding: 8px 15px;
                    font-weight: bold;
                    min-width: 100px;
                    font-family: 'Roboto Medium', 'Segoe UI', 'Arial', sans-serif;
                    
                }}
                QPushButton:hover {{
                    background-color: {VTN_YELLOW_HOVER};
                }}
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        tools_layout.addStretch()
        tools_layout.addWidget(self.add_button)
        tools_layout.addWidget(self.history_button)
        tools_layout.addWidget(self.refresh_button)
        
        layout.addWidget(tools_frame)
        
        # Khu vực hiển thị bảng giá
        content_frame = QFrame()
        content_frame.setStyleSheet(f"background-color: {VTN_DARKER_BG}; border-radius: 6px;")
        content_layout = QVBoxLayout(content_frame)
        
        self.current_price_label = QLabel("BẢNG GIÁ HIỆN TẠI")
        self.current_price_label.setFont(QFont("Roboto", 11, QFont.Weight.Bold))
        self.current_price_label.setStyleSheet(f"color: {VTN_ORANGE}; padding: 5px;")
        content_layout.addWidget(self.current_price_label)
        
        # Bảng hiển thị bảng giá hiện tại
        self.current_table = QTableWidget()
        self.current_table.setColumnCount(3)
        self.current_table.setHorizontalHeaderLabels(["Bậc thang", "Định mức (kWh)", "Đơn giá (đ/kWh)"])
        self.current_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.current_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.current_table.setAlternatingRowColors(True)
        self.current_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 4px;
                background-color: {VTN_DARK_BG};
                gridline-color: {VTN_GRAY_BORDER};
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: {VTN_YELLOW};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {VTN_DARKER_BG};
                color: {VTN_YELLOW};
                padding: 5px;
                border: 1px solid {VTN_GRAY_BORDER};
                font-weight: bold;
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
        """)
        content_layout.addWidget(self.current_table)
        
        # Thông tin bảng giá hiện tại
        self.current_info_frame = QFrame()
        info_layout = QHBoxLayout(self.current_info_frame)
        
        self.current_date_label = QLabel("Ngày áp dụng: --/--/----")
        self.current_date_label.setStyleSheet(f"font-weight: bold; color: {VTN_LIGHT_TEXT}; font-family: 'Roboto', 'Arial', sans-serif;")
        
        self.current_vat_label = QLabel("Thuế VAT: 10%")
        self.current_vat_label.setStyleSheet(f"font-weight: bold; color: {VTN_LIGHT_TEXT}; font-family: 'Roboto', 'Arial', sans-serif;")
        
        info_layout.addWidget(self.current_date_label)
        info_layout.addStretch()
        info_layout.addWidget(self.current_vat_label)
        
        content_layout.addWidget(self.current_info_frame)
        
        # Bảng hiển thị lịch sử bảng giá
        self.history_label = QLabel("LỊCH SỬ BẢNG GIÁ")
        self.history_label.setFont(QFont("Roboto", 11, QFont.Weight.Bold))
        self.history_label.setStyleSheet(f"color: {VTN_ORANGE}; padding: 5px;")
        self.history_label.setVisible(False)
        content_layout.addWidget(self.history_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["Mã bảng giá", "Ngày áp dụng", "Thuế VAT"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setStyleSheet(f"""
            QTableWidget {{
                border: 1px solid {VTN_GRAY_BORDER};
                border-radius: 4px;
                background-color: {VTN_DARK_BG};
                gridline-color: {VTN_GRAY_BORDER};
                color: {VTN_LIGHT_TEXT};
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: {VTN_YELLOW};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {VTN_DARKER_BG};
                color: {VTN_YELLOW};
                padding: 5px;
                border: 1px solid {VTN_GRAY_BORDER};
                font-weight: bold;
                font-family: 'Roboto', 'Arial', sans-serif;
            }}
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
        try:
            self.load_current_bang_gia()
            
            # Nếu đang hiển thị lịch sử, cập nhật lịch sử bảng giá
            if self.history_table.isVisible():
                self.load_bang_gia_history()
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể tải dữ liệu bảng giá: {str(e)}")
    
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