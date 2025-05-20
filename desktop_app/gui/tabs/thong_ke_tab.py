#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
                           QComboBox, QDateEdit, QGroupBox, QTabWidget,
                           QHeaderView, QRadioButton, QButtonGroup, QFileDialog,
                           QMessageBox)
from PyQt6.QtCore import Qt, QDate, QSizeF
from PyQt6.QtGui import QIcon, QFont

import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QTextDocument
from PyQt6.QtCore import QSize, QRectF, QPoint, QSizeF

class ThongKeTab(QWidget):
    """
    Tab thống kê và báo cáo
    """
    
    def __init__(self, db):
        """
        Khởi tạo tab thống kê
        
        Args:
            db (DatabaseHandler): Đối tượng xử lý dữ liệu
        """
        super().__init__()
        
        self.db = db
        self.init_ui()
        
    def init_ui(self):
        """Khởi tạo giao diện tab thống kê"""
        layout = QVBoxLayout(self)
        
        # Tạo tab widget
        self.thong_ke_tabs = QTabWidget()
        
        # Tạo các tab con
        self.tieu_thu_tab = QWidget()
        self.doanh_thu_tab = QWidget()
        self.bao_cao_tab = QWidget()
        
        # Thiết lập giao diện cho mỗi tab
        self.setup_tieu_thu_tab()
        self.setup_doanh_thu_tab()
        self.setup_bao_cao_tab()
        
        # Thêm các tab vào tab widget
        self.thong_ke_tabs.addTab(self.tieu_thu_tab, "Thống kê tiêu thụ")
        self.thong_ke_tabs.addTab(self.doanh_thu_tab, "Thống kê doanh thu")
        self.thong_ke_tabs.addTab(self.bao_cao_tab, "Báo cáo")
        
        # Kết nối sự kiện thay đổi tab
        self.thong_ke_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Thêm tab widget vào layout chính
        layout.addWidget(self.thong_ke_tabs)
        
        # Cập nhật biểu đồ ban đầu cho tab đầu tiên
        self.update_tieu_thu_chart()
        
        # Cập nhật báo cáo ban đầu
        self.generate_report()
    
    def setup_tieu_thu_tab(self):
        """Thiết lập tab thống kê tiêu thụ điện"""
        layout = QVBoxLayout(self.tieu_thu_tab)
        
        # Khu vực bộ lọc
        filter_group = QGroupBox("Bộ lọc")
        filter_layout = QHBoxLayout(filter_group)
        
        # Chọn loại thống kê
        self.tieu_thu_type_combo = QComboBox()
        self.tieu_thu_type_combo.addItems(["Theo tháng", "Theo quý", "Theo năm"])
        
        # Chọn năm
        self.tieu_thu_year_combo = QComboBox()
        current_year = datetime.datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            self.tieu_thu_year_combo.addItem(str(year))
        self.tieu_thu_year_combo.setCurrentText(str(current_year))
        
        # Nút áp dụng
        self.tieu_thu_apply_button = QPushButton("Áp dụng")
        self.tieu_thu_apply_button.clicked.connect(self.update_tieu_thu_chart)
        
        # Nút xuất báo cáo
        self.tieu_thu_export_button = QPushButton("Xuất báo cáo")
        self.tieu_thu_export_button.clicked.connect(self.export_tieu_thu_report)
        
        # Thêm các controls vào layout
        filter_layout.addWidget(QLabel("Loại thống kê:"))
        filter_layout.addWidget(self.tieu_thu_type_combo)
        filter_layout.addWidget(QLabel("Năm:"))
        filter_layout.addWidget(self.tieu_thu_year_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(self.tieu_thu_apply_button)
        filter_layout.addWidget(self.tieu_thu_export_button)
        
        layout.addWidget(filter_group)
        
        # Tạo khu vực hiển thị biểu đồ
        self.tieu_thu_plot_widget = QWidget()
        self.tieu_thu_plot_layout = QVBoxLayout(self.tieu_thu_plot_widget)
        
        # Tạo biểu đồ trống
        self.tieu_thu_figure = Figure(figsize=(8, 5))
        self.tieu_thu_canvas = FigureCanvas(self.tieu_thu_figure)
        self.tieu_thu_plot_layout.addWidget(self.tieu_thu_canvas)
        
        layout.addWidget(self.tieu_thu_plot_widget)
    
    def setup_doanh_thu_tab(self):
        """Thiết lập tab thống kê doanh thu"""
        layout = QVBoxLayout(self.doanh_thu_tab)
        
        # Khu vực bộ lọc
        filter_group = QGroupBox("Bộ lọc")
        filter_layout = QHBoxLayout(filter_group)
        
        # Chọn loại thống kê
        self.doanh_thu_type_combo = QComboBox()
        self.doanh_thu_type_combo.addItems(["Theo tháng", "Theo quý", "Theo năm"])
        
        # Chọn năm
        self.doanh_thu_year_combo = QComboBox()
        current_year = datetime.datetime.now().year
        for year in range(current_year - 5, current_year + 1):
            self.doanh_thu_year_combo.addItem(str(year))
        self.doanh_thu_year_combo.setCurrentText(str(current_year))
        
        # Nút áp dụng
        self.doanh_thu_apply_button = QPushButton("Áp dụng")
        self.doanh_thu_apply_button.clicked.connect(self.update_doanh_thu_chart)
        
        # Nút xuất báo cáo
        self.doanh_thu_export_button = QPushButton("Xuất báo cáo")
        self.doanh_thu_export_button.clicked.connect(self.export_doanh_thu_report)
        
        # Thêm các controls vào layout
        filter_layout.addWidget(QLabel("Loại thống kê:"))
        filter_layout.addWidget(self.doanh_thu_type_combo)
        filter_layout.addWidget(QLabel("Năm:"))
        filter_layout.addWidget(self.doanh_thu_year_combo)
        filter_layout.addStretch()
        filter_layout.addWidget(self.doanh_thu_apply_button)
        filter_layout.addWidget(self.doanh_thu_export_button)
        
        layout.addWidget(filter_group)
        
        # Tạo khu vực hiển thị biểu đồ
        self.doanh_thu_plot_widget = QWidget()
        self.doanh_thu_plot_layout = QVBoxLayout(self.doanh_thu_plot_widget)
        
        # Tạo biểu đồ trống
        self.doanh_thu_figure = Figure(figsize=(8, 5))
        self.doanh_thu_canvas = FigureCanvas(self.doanh_thu_figure)
        self.doanh_thu_plot_layout.addWidget(self.doanh_thu_canvas)
        
        layout.addWidget(self.doanh_thu_plot_widget)
    
    def setup_bao_cao_tab(self):
        """Thiết lập tab báo cáo"""
        layout = QVBoxLayout(self.bao_cao_tab)
        
        # Khu vực chọn loại báo cáo
        report_type_group = QGroupBox("Loại Báo Cáo")
        report_type_layout = QVBoxLayout(report_type_group)
        
        # Radio buttons cho các loại báo cáo
        self.report_type_group = QButtonGroup()
        
        self.khach_hang_tieu_thu_radio = QRadioButton("Khách hàng tiêu thụ nhiều nhất")
        self.khach_hang_tieu_thu_radio.setChecked(True)
        
        self.hoa_don_chua_thanh_toan_radio = QRadioButton("Hóa đơn chưa thanh toán")
        self.hoa_don_qua_han_radio = QRadioButton("Hóa đơn quá hạn thanh toán")
        self.doanh_thu_theo_khu_vuc_radio = QRadioButton("Doanh thu theo khu vực")
        
        # Thêm các radio button vào group
        self.report_type_group.addButton(self.khach_hang_tieu_thu_radio)
        self.report_type_group.addButton(self.hoa_don_chua_thanh_toan_radio)
        self.report_type_group.addButton(self.hoa_don_qua_han_radio)
        self.report_type_group.addButton(self.doanh_thu_theo_khu_vuc_radio)
        
        # Thêm vào layout
        report_type_layout.addWidget(self.khach_hang_tieu_thu_radio)
        report_type_layout.addWidget(self.hoa_don_chua_thanh_toan_radio)
        report_type_layout.addWidget(self.hoa_don_qua_han_radio)
        report_type_layout.addWidget(self.doanh_thu_theo_khu_vuc_radio)
        
        layout.addWidget(report_type_group)
        
        # Nút tạo báo cáo
        button_layout = QHBoxLayout()
        
        self.generate_report_button = QPushButton("Tạo báo cáo")
        self.generate_report_button.clicked.connect(self.generate_report)
        
        # Thêm nút xuất báo cáo PDF
        self.export_pdf_button = QPushButton("Xuất PDF")
        self.export_pdf_button.clicked.connect(self.export_report_to_pdf)
        
        button_layout.addStretch()
        button_layout.addWidget(self.generate_report_button)
        button_layout.addWidget(self.export_pdf_button)
        
        layout.addLayout(button_layout)
        
        # Khu vực hiển thị báo cáo
        self.report_table = QTableWidget()
        
        # Cài đặt thuộc tính bảng để cột mở rộng đầy đủ
        self.report_table.horizontalHeader().setMinimumSectionSize(80)
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Hiển thị đường kẻ lưới đầy đủ
        self.report_table.setShowGrid(True)
        
        # Cho phép bảng chiếm nhiều không gian hơn trong tab
        self.report_table.setMinimumHeight(300)
        
        layout.addWidget(self.report_table)
        
        # Tạo báo cáo ban đầu
        self.generate_report()
    
    def on_tab_changed(self, index):
        """
        Xử lý sự kiện khi thay đổi tab thống kê
        
        Args:
            index (int): Chỉ số tab được chọn
        """
        tab_widget = self.thong_ke_tabs.widget(index)
        
        if tab_widget == self.tieu_thu_tab:
            self.update_tieu_thu_chart()
        elif tab_widget == self.doanh_thu_tab:
            self.update_doanh_thu_chart()
        elif tab_widget == self.bao_cao_tab:
            # Chuẩn bị dữ liệu cho báo cáo mặc định
            self.generate_report()
    
    def update_tieu_thu_chart(self):
        """Cập nhật biểu đồ thống kê tiêu thụ điện"""
        # Lấy loại thống kê và năm
        stat_type = self.tieu_thu_type_combo.currentText()
        year = int(self.tieu_thu_year_combo.currentText())
        
        # Lấy dữ liệu thật từ cơ sở dữ liệu
        if stat_type == "Theo tháng":
            # Lấy dữ liệu tiêu thụ theo từng tháng trong năm
            data = self.db.thong_ke_tieu_thu_theo_nam(nam=year)
            x_labels = [f"Tháng {i}" for i in range(1, 13)]
            y_values = []
            
            for thang in range(1, 13):
                if str(thang) in data["theo_thang"] or thang in data["theo_thang"]:
                    # Kiểm tra nếu khóa là chuỗi hoặc số nguyên
                    if str(thang) in data["theo_thang"]:
                        y_values.append(data["theo_thang"][str(thang)]["tieu_thu"])
                    else:
                        y_values.append(data["theo_thang"][thang]["tieu_thu"])
                else:
                    y_values.append(0)
                    
            x_ticks = range(len(x_labels))
            title = f"Thống kê lượng điện tiêu thụ theo tháng - Năm {year}"
        elif stat_type == "Theo quý":
            # Lấy dữ liệu tiêu thụ theo từng tháng và tổng hợp theo quý
            data = self.db.thong_ke_tieu_thu_theo_nam(nam=year)
            x_labels = [f"Quý {i}" for i in range(1, 5)]
            y_values = [0, 0, 0, 0]  # 4 quý
            
            for thang in range(1, 13):
                if str(thang) in data["theo_thang"] or thang in data["theo_thang"]:
                    quy = (thang - 1) // 3
                    if str(thang) in data["theo_thang"]:
                        y_values[quy] += data["theo_thang"][str(thang)]["tieu_thu"]
                    else:
                        y_values[quy] += data["theo_thang"][thang]["tieu_thu"]
                    
            x_ticks = range(len(x_labels))
            title = f"Thống kê lượng điện tiêu thụ theo quý - Năm {year}"
        else:  # Theo năm
            # Lấy dữ liệu tiêu thụ cho 5 năm gần nhất
            current_year = datetime.datetime.now().year
            start_year = current_year - 4
            x_labels = [str(y) for y in range(start_year, current_year + 1)]
            y_values = []
            
            for y in range(start_year, current_year + 1):
                data = self.db.thong_ke_tieu_thu_theo_nam(nam=y)
                y_values.append(data["tong_tieu_thu"])
                
            x_ticks = range(len(x_labels))
            title = "Thống kê lượng điện tiêu thụ theo năm"
        
        # Vẽ biểu đồ
        self.tieu_thu_figure.clear()
        ax = self.tieu_thu_figure.add_subplot(111)
        
        # Vẽ biểu đồ cột
        bars = ax.bar(x_ticks, y_values, width=0.6, color='skyblue', edgecolor='black')
        
        # Thêm giá trị lên đầu mỗi cột
        for bar, value in zip(bars, y_values):
            height = bar.get_height()
            if height > 0:  # Chỉ hiển thị giá trị > 0
                ax.text(bar.get_x() + bar.get_width() / 2, height + 5, str(int(value)), 
                        ha='center', va='bottom')
        
        # Đặt tiêu đề và nhãn
        ax.set_title(title)
        ax.set_xlabel("Thời gian")
        ax.set_ylabel("Lượng điện tiêu thụ (kWh)")
        
        # Đặt nhãn trục x
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        
        # Thêm lưới
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Cập nhật biểu đồ
        self.tieu_thu_canvas.draw()
    
    def update_doanh_thu_chart(self):
        """Cập nhật biểu đồ thống kê doanh thu"""
        # Lấy loại thống kê và năm
        stat_type = self.doanh_thu_type_combo.currentText()
        year = int(self.doanh_thu_year_combo.currentText())
        
        # Lấy dữ liệu thật từ cơ sở dữ liệu
        if stat_type == "Theo tháng":
            # Lấy dữ liệu doanh thu theo từng tháng trong năm
            data = self.db.thong_ke_doanh_thu_theo_nam(nam=year)
            x_labels = [f"Tháng {i}" for i in range(1, 13)]
            y_values = []
            
            for thang in range(1, 13):
                if str(thang) in data["theo_thang"] or thang in data["theo_thang"]:
                    # Chuyển đổi từ VND sang triệu VND
                    if str(thang) in data["theo_thang"]:
                        y_values.append(data["theo_thang"][str(thang)]["doanh_thu"] / 1000000)
                    else:
                        y_values.append(data["theo_thang"][thang]["doanh_thu"] / 1000000)
                else:
                    y_values.append(0)
                    
            x_ticks = range(len(x_labels))
            title = f"Thống kê doanh thu theo tháng - Năm {year}"
        elif stat_type == "Theo quý":
            # Lấy dữ liệu doanh thu theo từng tháng và tổng hợp theo quý
            data = self.db.thong_ke_doanh_thu_theo_nam(nam=year)
            x_labels = [f"Quý {i}" for i in range(1, 5)]
            y_values = [0, 0, 0, 0]  # 4 quý
            
            for thang in range(1, 13):
                if str(thang) in data["theo_thang"] or thang in data["theo_thang"]:
                    quy = (thang - 1) // 3
                    # Chuyển đổi từ VND sang triệu VND
                    if str(thang) in data["theo_thang"]:
                        y_values[quy] += data["theo_thang"][str(thang)]["doanh_thu"] / 1000000
                    else:
                        y_values[quy] += data["theo_thang"][thang]["doanh_thu"] / 1000000
                    
            x_ticks = range(len(x_labels))
            title = f"Thống kê doanh thu theo quý - Năm {year}"
        else:  # Theo năm
            # Lấy dữ liệu doanh thu cho 5 năm gần nhất
            current_year = datetime.datetime.now().year
            start_year = current_year - 4
            x_labels = [str(y) for y in range(start_year, current_year + 1)]
            y_values = []
            
            for y in range(start_year, current_year + 1):
                data = self.db.thong_ke_doanh_thu_theo_nam(nam=y)
                # Chuyển đổi từ VND sang triệu VND
                y_values.append(data["tong_doanh_thu"] / 1000000)
                
            x_ticks = range(len(x_labels))
            title = "Thống kê doanh thu theo năm"
        
        # Vẽ biểu đồ
        self.doanh_thu_figure.clear()
        ax = self.doanh_thu_figure.add_subplot(111)
        
        # Vẽ biểu đồ cột
        bars = ax.bar(x_ticks, y_values, width=0.6, color='lightgreen', edgecolor='black')
        
        # Thêm giá trị lên đầu mỗi cột
        for bar, value in zip(bars, y_values):
            height = bar.get_height()
            if height > 0:  # Chỉ hiển thị giá trị > 0
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.1, f"{value:.1f}", 
                        ha='center', va='bottom')
        
        # Đặt tiêu đề và nhãn
        ax.set_title(title)
        ax.set_xlabel("Thời gian")
        ax.set_ylabel("Doanh thu (triệu VNĐ)")
        
        # Đặt nhãn trục x
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        
        # Thêm lưới
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Cập nhật biểu đồ
        self.doanh_thu_canvas.draw()
    
    def generate_report(self):
        """Tạo báo cáo theo loại được chọn"""
        try:
            # Xác định loại báo cáo
            if self.khach_hang_tieu_thu_radio.isChecked():
                self.generate_top_customers_report()
            elif self.hoa_don_chua_thanh_toan_radio.isChecked():
                self.generate_unpaid_invoices_report()
            elif self.hoa_don_qua_han_radio.isChecked():
                self.generate_overdue_invoices_report()
            elif self.doanh_thu_theo_khu_vuc_radio.isChecked():
                self.generate_revenue_by_area_report()
                
            # Đảm bảo bảng được cập nhật đúng
            self.adjust_table_columns()
            
        except Exception as e:
            print(f"Lỗi khi tạo báo cáo: {e}")
            # Hiển thị thông báo lỗi
            QMessageBox.warning(self, "Lỗi", f"Không thể tạo báo cáo.\nLỗi: {str(e)}")
            
    def adjust_table_columns(self):
        """Điều chỉnh chiều rộng cột của bảng để hiển thị tối ưu"""
        # Tự động điều chỉnh chiều rộng cột dựa trên nội dung
        self.report_table.resizeColumnsToContents()
        self.report_table.resizeRowsToContents()
        
        # Tính toán tổng chiều rộng của tất cả các cột
        total_width = 0
        for col in range(self.report_table.columnCount()):
            total_width += self.report_table.columnWidth(col)
        
        # Lấy chiều rộng hiện tại của bảng
        table_width = self.report_table.width()
        
        # Thiết lập chiều rộng tối thiểu cho các cột
        min_widths = {
            0: 50,  # STT
            1: 120,  # Mã khách hàng/hóa đơn
            2: 200,  # Tên khách hàng
        }
        
        # Áp dụng chiều rộng tối thiểu
        for col, min_width in min_widths.items():
            if col < self.report_table.columnCount():
                current_width = self.report_table.columnWidth(col)
                if current_width < min_width:
                    self.report_table.setColumnWidth(col, min_width)
        
        # Cập nhật tổng chiều rộng sau khi áp dụng các chiều rộng tối thiểu
        total_width = 0
        for col in range(self.report_table.columnCount()):
            total_width += self.report_table.columnWidth(col)
        
        # Nếu tổng chiều rộng của các cột nhỏ hơn chiều rộng bảng, 
        # cần mở rộng các cột để lấp đầy bảng
        if total_width < table_width:
            # Tính toán không gian còn lại
            remaining_width = table_width - total_width
            
            # Phân phối không gian còn lại cho các cột theo tỷ lệ
            for col in range(self.report_table.columnCount()):
                if col not in min_widths or col >= 3:  # Chỉ mở rộng các cột không phải STT, mã và tên
                    current_width = self.report_table.columnWidth(col)
                    extra_width = int(remaining_width / (self.report_table.columnCount() - min(3, len(min_widths))))
                    new_width = current_width + extra_width
                    self.report_table.setColumnWidth(col, new_width)
        
        # Đảm bảo bảng được kéo dãn đầy đủ
        self.report_table.horizontalHeader().setStretchLastSection(True)
    
    def generate_top_customers_report(self):
        """Tạo báo cáo khách hàng tiêu thụ nhiều nhất"""
        # Thiết lập bảng
        self.report_table.setRowCount(0)
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "STT", "Mã khách hàng", "Tên khách hàng", "Tổng tiêu thụ (kWh)", "Tổng tiền (VNĐ)"
        ])
        
        try:
            # Lấy danh sách tất cả các hóa đơn
            hoa_don_list = self.db.get_all_hoa_don()
            
            if not hoa_don_list:
                # Hiển thị thông báo nếu không có dữ liệu
                self.report_table.setRowCount(1)
                self.report_table.setSpan(0, 0, 1, 5)
                self.report_table.setItem(0, 0, QTableWidgetItem("Không có dữ liệu hóa đơn để tạo báo cáo"))
                return
            
            # Tạo dict để tính tổng tiêu thụ và tổng tiền cho mỗi khách hàng
            khach_hang_stats = {}
            
            for hd in hoa_don_list:
                ma_khach_hang = hd.ma_khach_hang
                # Sử dụng thuộc tính tieu_thu hoặc dien_tieu_thu để lấy giá trị chính xác
                tieu_thu = hd.tieu_thu
                tong_tien = hd.so_tien if hd.so_tien else 0
                
                if ma_khach_hang in khach_hang_stats:
                    khach_hang_stats[ma_khach_hang]["tieu_thu"] += tieu_thu
                    khach_hang_stats[ma_khach_hang]["tong_tien"] += tong_tien
                else:
                    khach_hang = self.db.get_khach_hang(ma_khach_hang)
                    ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không xác định"
                    khach_hang_stats[ma_khach_hang] = {
                        "ma_khach_hang": ma_khach_hang,
                        "ten_khach_hang": ten_khach_hang,
                        "tieu_thu": tieu_thu,
                        "tong_tien": tong_tien
                    }
            
            if not khach_hang_stats:
                self.report_table.setRowCount(1)
                self.report_table.setSpan(0, 0, 1, 5)
                self.report_table.setItem(0, 0, QTableWidgetItem("Không có dữ liệu để hiển thị"))
                return
            
            # Chuyển thành list và sắp xếp theo tiêu thụ giảm dần
            top_customers = sorted(
                khach_hang_stats.values(),
                key=lambda x: x["tieu_thu"],
                reverse=True
            )
            
            # Thêm dữ liệu vào bảng
            for row, kh in enumerate(top_customers):
                self.report_table.insertRow(row)
                self.report_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.report_table.setItem(row, 1, QTableWidgetItem(kh["ma_khach_hang"]))
                self.report_table.setItem(row, 2, QTableWidgetItem(kh["ten_khach_hang"]))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{kh['tieu_thu']:,}"))
                self.report_table.setItem(row, 4, QTableWidgetItem(f"{int(kh['tong_tien']):,}"))
                
                # Giới hạn chỉ hiển thị 10 người dùng
                if row >= 9:
                    break
                    
        except Exception as e:
            print(f"Lỗi khi tạo báo cáo khách hàng: {e}")
            self.report_table.setRowCount(1)
            self.report_table.setSpan(0, 0, 1, 5)
            self.report_table.setItem(0, 0, QTableWidgetItem(f"Lỗi khi tạo báo cáo: {str(e)}"))
    
    def generate_unpaid_invoices_report(self):
        """Tạo báo cáo hóa đơn chưa thanh toán"""
        # Thiết lập bảng
        self.report_table.setRowCount(0)
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "STT", "Mã hóa đơn", "Khách hàng", "Tháng/Năm", "Số tiền (VNĐ)"
        ])
        
        try:
            # Lấy danh sách hóa đơn chưa thanh toán
            hoa_don_list = self.db.get_hoa_don_chua_thanh_toan()
            
            if not hoa_don_list:
                # Hiển thị thông báo nếu không có dữ liệu
                self.report_table.setRowCount(1)
                self.report_table.setSpan(0, 0, 1, 5)
                self.report_table.setItem(0, 0, QTableWidgetItem("Không có hóa đơn chưa thanh toán"))
                return
            
            # Thêm dữ liệu vào bảng
            for row, hd in enumerate(hoa_don_list):
                # Lấy thông tin khách hàng
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không xác định"
                
                self.report_table.insertRow(row)
                self.report_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.report_table.setItem(row, 1, QTableWidgetItem(hd.ma_hoa_don))
                self.report_table.setItem(row, 2, QTableWidgetItem(ten_khach_hang))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{hd.thang}/{hd.nam}"))
                
                # Định dạng số tiền (hiển thị số nguyên)
                so_tien = hd.so_tien if hd.so_tien else 0
                self.report_table.setItem(row, 4, QTableWidgetItem(f"{int(so_tien):,}"))
                
        except Exception as e:
            print(f"Lỗi khi tạo báo cáo hóa đơn chưa thanh toán: {e}")
            self.report_table.setRowCount(1)
            self.report_table.setSpan(0, 0, 1, 5)
            self.report_table.setItem(0, 0, QTableWidgetItem(f"Lỗi khi tạo báo cáo: {str(e)}"))
    
    def generate_overdue_invoices_report(self):
        """Tạo báo cáo hóa đơn quá hạn thanh toán"""
        # Thiết lập bảng
        self.report_table.setRowCount(0)
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "STT", "Mã hóa đơn", "Khách hàng", "Tháng/Năm", "Số tiền (VNĐ)", "Số ngày quá hạn"
        ])
        
        try:
            # Lấy danh sách hóa đơn quá hạn
            hoa_don_list = self.db.get_hoa_don_qua_han()
            
            if not hoa_don_list:
                # Hiển thị thông báo nếu không có dữ liệu
                self.report_table.setRowCount(1)
                self.report_table.setSpan(0, 0, 1, 6)
                self.report_table.setItem(0, 0, QTableWidgetItem("Không có hóa đơn quá hạn"))
                return
            
            # Thêm dữ liệu vào bảng
            for row, hd in enumerate(hoa_don_list):
                # Lấy thông tin khách hàng
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không xác định"
                
                self.report_table.insertRow(row)
                self.report_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.report_table.setItem(row, 1, QTableWidgetItem(hd.ma_hoa_don))
                self.report_table.setItem(row, 2, QTableWidgetItem(ten_khach_hang))
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{hd.thang}/{hd.nam}"))
                
                # Định dạng số tiền (hiển thị số nguyên)
                so_tien = hd.so_tien if hd.so_tien else 0
                self.report_table.setItem(row, 4, QTableWidgetItem(f"{int(so_tien):,}"))
                
                # Hiển thị số ngày quá hạn với màu đỏ
                ngay_qua_han_item = QTableWidgetItem(str(hd.ngay_qua_han))
                ngay_qua_han_item.setForeground(Qt.GlobalColor.darkRed)
                self.report_table.setItem(row, 5, ngay_qua_han_item)
                
        except Exception as e:
            print(f"Lỗi khi tạo báo cáo hóa đơn quá hạn: {e}")
            self.report_table.setRowCount(1)
            self.report_table.setSpan(0, 0, 1, 6)
            self.report_table.setItem(0, 0, QTableWidgetItem(f"Lỗi khi tạo báo cáo: {str(e)}"))
    
    def generate_revenue_by_area_report(self):
        """Tạo báo cáo doanh thu theo khu vực"""
        # Thiết lập bảng
        self.report_table.setRowCount(0)
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels([
            "STT", "Khu vực", "Số khách hàng", "Doanh thu (VNĐ)"
        ])
        
        try:
            # Lấy danh sách tất cả khách hàng
            khach_hang_list = self.db.get_all_khach_hang()
            
            if not khach_hang_list:
                # Hiển thị thông báo nếu không có dữ liệu
                self.report_table.setRowCount(1)
                self.report_table.setSpan(0, 0, 1, 4)
                self.report_table.setItem(0, 0, QTableWidgetItem("Không có dữ liệu khách hàng"))
                return
            
            # Tạo dict để tính tổng doanh thu và số lượng khách hàng theo khu vực
            khu_vuc_stats = {}
            
            for kh in khach_hang_list:
                khu_vuc = kh.dia_chi
                
                if not khu_vuc:
                    khu_vuc = "Không xác định"
                    
                # Khởi tạo nếu chưa có
                if khu_vuc not in khu_vuc_stats:
                    khu_vuc_stats[khu_vuc] = {
                        "so_khach_hang": 0,
                        "doanh_thu": 0
                    }
                
                # Cập nhật số khách hàng
                khu_vuc_stats[khu_vuc]["so_khach_hang"] += 1
                
                # Lấy danh sách hóa đơn của khách hàng này
                hoa_don_list = self.db.get_hoa_don_by_khach_hang(kh.ma_khach_hang)
                
                # Tính tổng doanh thu
                for hd in hoa_don_list:
                    khu_vuc_stats[khu_vuc]["doanh_thu"] += hd.so_tien if hd.so_tien else 0
            
            if not khu_vuc_stats:
                self.report_table.setRowCount(1)
                self.report_table.setSpan(0, 0, 1, 4)
                self.report_table.setItem(0, 0, QTableWidgetItem("Không có dữ liệu để hiển thị"))
                return
            
            # Chuyển thành list và sắp xếp theo doanh thu giảm dần
            khu_vuc_sorted = sorted(
                [{"khu_vuc": k, **v} for k, v in khu_vuc_stats.items()],
                key=lambda x: x["doanh_thu"],
                reverse=True
            )
            
            # Thêm dữ liệu vào bảng
            for row, khu_vuc in enumerate(khu_vuc_sorted):
                self.report_table.insertRow(row)
                self.report_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
                self.report_table.setItem(row, 1, QTableWidgetItem(khu_vuc["khu_vuc"]))
                self.report_table.setItem(row, 2, QTableWidgetItem(str(khu_vuc["so_khach_hang"])))
                # Định dạng số tiền thành số nguyên
                doanh_thu = khu_vuc["doanh_thu"] if khu_vuc["doanh_thu"] else 0
                self.report_table.setItem(row, 3, QTableWidgetItem(f"{int(doanh_thu):,}"))
                
        except Exception as e:
            print(f"Lỗi khi tạo báo cáo doanh thu theo khu vực: {e}")
            self.report_table.setRowCount(1)
            self.report_table.setSpan(0, 0, 1, 4)
            self.report_table.setItem(0, 0, QTableWidgetItem(f"Lỗi khi tạo báo cáo: {str(e)}"))
    
    def export_tieu_thu_report(self):
        """Xuất báo cáo thống kê tiêu thụ điện"""
        # Lấy loại thống kê và năm
        stat_type = self.tieu_thu_type_combo.currentText()
        year = self.tieu_thu_year_combo.currentText()
        
        # Chọn đường dẫn lưu file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu Báo Cáo", 
            f"Thong_ke_tieu_thu_{stat_type.replace(' ', '_')}_{year}.png",
            "Hình ảnh (*.png);;PDF (*.pdf)"
        )
        
        if file_path:
            # Lưu biểu đồ
            if file_path.endswith('.png'):
                self.tieu_thu_figure.savefig(file_path, dpi=300, bbox_inches='tight')
            elif file_path.endswith('.pdf'):
                self.tieu_thu_figure.savefig(file_path, format='pdf', bbox_inches='tight')
                
            # Thông báo thành công
            QMessageBox.information(self, "Thông báo", f"Đã xuất báo cáo thành công!\nĐường dẫn: {file_path}")
    
    def export_doanh_thu_report(self):
        """Xuất báo cáo thống kê doanh thu"""
        # Lấy loại thống kê và năm
        stat_type = self.doanh_thu_type_combo.currentText()
        year = self.doanh_thu_year_combo.currentText()
        
        # Chọn đường dẫn lưu file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Lưu Báo Cáo", 
            f"Thong_ke_doanh_thu_{stat_type.replace(' ', '_')}_{year}.png",
            "Hình ảnh (*.png);;PDF (*.pdf)"
        )
        
        if file_path:
            # Lưu biểu đồ
            if file_path.endswith('.png'):
                self.doanh_thu_figure.savefig(file_path, dpi=300, bbox_inches='tight')
            elif file_path.endswith('.pdf'):
                self.doanh_thu_figure.savefig(file_path, format='pdf', bbox_inches='tight')
                
            # Thông báo thành công
            QMessageBox.information(self, "Thông báo", f"Đã xuất báo cáo thành công!\nĐường dẫn: {file_path}")

    def export_report_to_pdf(self):
        """Xuất báo cáo thống kê dưới dạng PDF"""
        try:
            # Tạo báo cáo hiện tại
            self.generate_report()
            
            # Lấy đường dẫn lưu file
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Lưu Báo Cáo", 
                f"Bao_cao_{self.report_type_group.checkedButton().text().replace(' ', '_')}.pdf",
                "PDF (*.pdf)"
            )
            
            if not file_path:
                return
            
            # Sử dụng ReportLab để tạo PDF giống như hoa_don_pdf.py
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.units import mm
            from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
            from reportlab.platypus.frames import Frame
            import os
            import datetime
            
            # Màu chủ đạo giống với hoa_don_pdf.py
            VTN_YELLOW = colors.Color(1, 0.7, 0, 1)  # Màu vàng đậm
            VTN_GRAY = colors.Color(0.9, 0.9, 0.9, 1)  # Màu xám đậm hơn
            
            # Tạo class DocTemplate tùy chỉnh để thêm màu nền giống cmd
            class ReportPDFTemplate(BaseDocTemplate):
                def __init__(self, filename, **kw):
                    self.allowSplitting = 0
                    BaseDocTemplate.__init__(self, filename, **kw)
                    template = PageTemplate('normal', [Frame(
                        self.leftMargin, self.bottomMargin, self.width, self.height, id='normal'
                    )], onPage=self.add_page_background)
                    self.addPageTemplates([template])
                
                def add_page_background(self, canvas, doc):
                    # Đặt màu nền xám cho toàn bộ trang
                    canvas.saveState()
                    canvas.setFillColor(VTN_GRAY)
                    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
                    canvas.restoreState()
            
            # Đăng ký font Roboto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Đăng ký font Regular
            font_regular_path = os.path.join(base_dir, 'font', 'Roboto-Regular.ttf')
            if not os.path.exists(font_regular_path):
                font_regular_path = os.path.join(base_dir, '..', 'font', 'Roboto-Regular.ttf')
                if not os.path.exists(font_regular_path):
                    font_regular_path = os.path.join(base_dir, '..', 'font', 'static', 'Roboto-Regular.ttf')
                    if not os.path.exists(font_regular_path):
                        print(f"Không tìm thấy font Roboto-Regular.ttf")
            
            # Đăng ký font Bold
            font_bold_path = os.path.join(base_dir, 'font', 'Roboto-Bold.ttf')
            if not os.path.exists(font_bold_path):
                font_bold_path = os.path.join(base_dir, '..', 'font', 'Roboto-Bold.ttf')
                if not os.path.exists(font_bold_path):
                    font_bold_path = os.path.join(base_dir, '..', 'font', 'static', 'Roboto-Bold.ttf')
                    if not os.path.exists(font_bold_path):
                        print(f"Không tìm thấy font Roboto-Bold.ttf")
                        font_bold_path = font_regular_path
            
            # Đăng ký các font nếu tìm thấy
            if os.path.exists(font_regular_path):
                pdfmetrics.registerFont(TTFont('Roboto', font_regular_path))
            
            if os.path.exists(font_bold_path):
                pdfmetrics.registerFont(TTFont('Roboto-Bold', font_bold_path))
            
            # Tạo document với nền màu xám
            doc = ReportPDFTemplate(file_path, pagesize=A4,
                               rightMargin=20, leftMargin=20,
                               topMargin=20, bottomMargin=20)
            
            # Danh sách các phần tử
            elements = []
            
            # Tạo style cho các phần văn bản
            styles = getSampleStyleSheet()
            
            # Xác định font chính
            main_font = 'Roboto' if 'Roboto' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
            bold_font = 'Roboto-Bold' if 'Roboto-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
            
            # Style cho tiêu đề - màu vàng VTN
            title_style = ParagraphStyle(
                name='Title_Style',
                fontName=bold_font,
                fontSize=14,
                alignment=1,
                spaceAfter=10,
                textColor=VTN_YELLOW
            )
            
            # Style cho subtitle - màu vàng VTN và căn giữa
            subtitle_style = ParagraphStyle(
                name='Subtitle_Style',
                fontName=main_font,
                fontSize=10,
                alignment=1,
                spaceAfter=10,
                textColor=VTN_YELLOW
            )
            
            # Style cho heading
            heading_style = ParagraphStyle(
                name='Heading_Style',
                fontName=bold_font,
                fontSize=11,
                leading=14,
                textColor=colors.black
            )
            
            # Style cho company text đậm - màu vàng VTN
            company_style = ParagraphStyle(
                name='Company_Style',
                fontName=bold_font,
                fontSize=10,
                leading=14,
                textColor=VTN_YELLOW
            )
            
            # Style cho thông tin khách hàng - màu vàng
            customer_style = ParagraphStyle(
                name='Customer_Style',
                fontName=bold_font,
                fontSize=10,
                leading=14,
                textColor=VTN_YELLOW
            )
            
            # Style cho giá trị thông tin - màu đen
            value_style = ParagraphStyle(
                name='Value_Style',
                fontName=main_font,
                fontSize=10,
                leading=14,
                textColor=colors.black
            )
            
            # Style cho footer
            footer_style = ParagraphStyle(
                name='Footer_Style',
                fontName=main_font,
                fontSize=8,
                leading=10,
                alignment=1,
                textColor=colors.black
            )
            
            # Tiêu đề báo cáo
            report_title = ""
            if self.khach_hang_tieu_thu_radio.isChecked():
                report_title = "BÁO CÁO KHÁCH HÀNG TIÊU THỤ NHIỀU NHẤT"
            elif self.hoa_don_chua_thanh_toan_radio.isChecked():
                report_title = "BÁO CÁO HÓA ĐƠN CHƯA THANH TOÁN"
            elif self.hoa_don_qua_han_radio.isChecked():
                report_title = "BÁO CÁO HÓA ĐƠN QUÁ HẠN THANH TOÁN"
            elif self.doanh_thu_theo_khu_vuc_radio.isChecked():
                report_title = "BÁO CÁO DOANH THU THEO KHU VỰC"
            
            # Tìm logo
            logo_path = os.path.join(base_dir, 'resources', 'images', 'logo.png')
            if not os.path.exists(logo_path):
                logo_path = os.path.join(base_dir, '..', 'imgs', 'vtn_vip.png')
            
            # Thêm header giống hoa_don_pdf.py
            if os.path.exists(logo_path):
                # Chuẩn bị logo
                logo = Image(logo_path, width=60, height=30, hAlign='LEFT')
                
                # Chuẩn bị tiêu đề
                title = Paragraph(report_title, title_style)
                subtitle = Paragraph("(Báo cáo thống kê)", subtitle_style)
                
                # Tạo bảng header
                header_data = [[logo, title], ['', subtitle]]
                header_table = Table(header_data, colWidths=[100, 380])
                header_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Logo căn trái
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Tiêu đề căn giữa
                    ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),  # Căn giữa theo chiều dọc
                    ('SPAN', (0, 0), (0, 1)),  # Gộp hai dòng cho logo
                    ('LEFTPADDING', (0, 0), (0, 0), 10),  # Padding bên trái cho logo
                    ('RIGHTPADDING', (0, 0), (0, 0), 10),  # Padding bên phải cho logo
                    ('TOPPADDING', (0, 0), (0, 0), 5),     # Padding trên cho logo
                    ('BOTTOMPADDING', (0, 0), (0, 0), 5),  # Padding dưới cho logo
                ]))
                elements.append(header_table)
            else:
                # Nếu không có logo, chỉ thêm tiêu đề
                elements.append(Paragraph(report_title, title_style))
                elements.append(Paragraph("(Báo cáo thống kê)", subtitle_style))
            
            elements.append(Spacer(1, 5))
            
            # Thêm thông tin công ty
            elements.append(Paragraph("CÔNG TY ĐIỆN LỰC VTN VIP", company_style))
            elements.append(Paragraph("Địa chỉ: <font color='black'>Hà Nội</font>", customer_style))
            elements.append(Paragraph("Điện thoại: <font color='black'>19009000</font> - MST: <font color='black'>0100100079</font>", customer_style))
            elements.append(Spacer(1, 5))
            
            # Thêm ngày tạo báo cáo
            elements.append(Paragraph(f"Ngày xuất báo cáo: <font color='black'>{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</font>", customer_style))
            elements.append(Spacer(1, 10))
            
            # Thêm tiêu đề bảng báo cáo
            elements.append(Paragraph("CHI TIẾT BÁO CÁO", heading_style))
            elements.append(Spacer(1, 5))
            
            # Chuẩn bị dữ liệu cho bảng
            table_data = []
            
            # Thêm tiêu đề cột
            headers = []
            for col in range(self.report_table.columnCount()):
                headers.append(self.report_table.horizontalHeaderItem(col).text())
            table_data.append(headers)
            
            # Thêm nội dung
            for row in range(self.report_table.rowCount()):
                row_data = []
                for col in range(self.report_table.columnCount()):
                    item = self.report_table.item(row, col)
                    if item is not None:
                        # Định dạng lại các số tiền và số lượng để tránh bị đè lên nhau
                        text = item.text()
                        try:
                            # Kiểm tra xem nội dung có phải số hay không
                            if "," in text:  # Nếu là số có định dạng dấu phẩy
                                # Loại bỏ dấu phẩy và chuyển thành số
                                cleaned_text = text.replace(",", "")
                                value = float(cleaned_text)
                                # Định dạng riêng cho cột tiền (VNĐ)
                                if "tiền" in headers[col].lower() or "VNĐ" in headers[col]:
                                    # Làm tròn về số nguyên cho tiền VNĐ
                                    text = f"{int(value):,}"
                                else:
                                    # Định dạng cho các số khác
                                    if value == int(value):  # Nếu là số nguyên
                                        text = f"{int(value):,}"
                                    else:
                                        # Loại bỏ số 0 thừa sau dấu thập phân
                                        text = f"{value:.2f}".rstrip('0').rstrip('.') if '.' in f"{value:.2f}" else f"{value:.2f}"
                                        text = f"{float(text):,}".replace('.0,', ',')
                            elif text.replace(".", "", 1).isdigit():  # Nếu là số thập phân
                                value = float(text)
                                if "tiền" in headers[col].lower() or "VNĐ" in headers[col]:
                                    # Làm tròn về số nguyên cho tiền VNĐ
                                    text = f"{int(value):,}"
                                else:
                                    # Định dạng cho các số khác
                                    if value == int(value):  # Nếu là số nguyên
                                        text = f"{int(value):,}"
                                    else:
                                        # Loại bỏ số 0 thừa sau dấu thập phân
                                        text = f"{value:.2f}".rstrip('0').rstrip('.') if '.' in f"{value:.2f}" else f"{value:.2f}"
                                        text = f"{float(text):,}".replace('.0,', ',')
                        except:
                            pass  # Nếu không phải số, giữ nguyên text
                        
                        row_data.append(text)
                    else:
                        row_data.append("")
                table_data.append(row_data)
            
            # Tạo bảng
            if len(table_data) > 1:  # Đảm bảo có dữ liệu
                # Tính toán chiều rộng cột tùy theo loại báo cáo
                col_widths = []
                
                if self.khach_hang_tieu_thu_radio.isChecked():
                    # STT, Mã KH, Tên KH, Tổng tiêu thụ, Tổng tiền
                    col_widths = [40, 115, 200, 90, 110]
                elif self.hoa_don_chua_thanh_toan_radio.isChecked():
                    # STT, Mã HĐ, Khách hàng, Tháng/Năm, Số tiền
                    col_widths = [40, 115, 180, 65, 110]
                elif self.hoa_don_qua_han_radio.isChecked():
                    # STT, Mã HĐ, Khách hàng, Tháng/Năm, Số tiền, Số ngày quá hạn
                    col_widths = [40, 90, 150, 65, 100, 65]
                elif self.doanh_thu_theo_khu_vuc_radio.isChecked():
                    # STT, Khu vực, Số lượng KH, Doanh thu
                    col_widths = [40, 250, 80, 110]
                
                # Nếu không có cài đặt cụ thể, tính toán chiều rộng tự động
                if not col_widths or len(col_widths) != len(headers):
                    page_width = A4[0] - 40  # Trừ margin
                    col_widths = [page_width / len(headers)] * len(headers)
                
                # Tạo và định dạng bảng
                table = Table(table_data, colWidths=col_widths)
                
                # Style cho bảng - giống với hoa_don_pdf.py
                table_style = TableStyle([
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), bold_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                ])
                
                # Thêm căn giữa cho cột STT
                table_style.add('ALIGN', (0, 1), (0, -1), 'CENTER')
                
                # Căn phải cho cột tiền và cột số lượng
                for col_idx, header in enumerate(headers):
                    if "VNĐ" in header or "tiền" in header.lower() or "lượng" in header.lower():
                        table_style.add('ALIGN', (col_idx, 1), (col_idx, -1), 'RIGHT')
                
                # Áp dụng style
                table.setStyle(table_style)
                elements.append(table)
                
                # Thêm kí tên giống hoa_don_pdf.py
                elements.append(Spacer(1, 20))
                
                ngay_phat_hanh = datetime.datetime.now().strftime("%d/%m/%Y")
                ky_ten_data = [
                    ['NGƯỜI LẬP BÁO CÁO', '', 'ĐẠI DIỆN ĐƠN VỊ'],
                    ['(Ký, ghi rõ họ tên)', '', f'Ngày {ngay_phat_hanh}'],
                    ['', '', ''],
                    ['', '', ''],
                    ['', '', ''],
                    ['', '', 'CÔNG TY ĐIỆN LỰC VTN VIP']
                ]
                ky_ten_table = Table(ky_ten_data, colWidths=[150, 100, 150])
                ky_ten_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), main_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                elements.append(ky_ten_table)
                
                # Xuất PDF
                doc.build(elements)
                
                # Thông báo thành công
                QMessageBox.information(self, "Xuất Báo Cáo", "Xuất báo cáo PDF thành công!\nĐường dẫn: " + file_path)
                
                # Mở file PDF
                import platform
                import subprocess
                
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', file_path))
                else:  # Linux
                    subprocess.call(('xdg-open', file_path))
            else:
                QMessageBox.warning(self, "Thông báo", "Không có dữ liệu để xuất báo cáo!")
            
        except Exception as e:
            print(f"Lỗi khi xuất báo cáo PDF: {e}")
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất báo cáo: {str(e)}") 