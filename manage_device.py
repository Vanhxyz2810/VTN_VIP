import sqlite3
import os
import sys
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QDialog, QFormLayout, QDateEdit)
from PyQt6.QtGui import QFont, QIcon, QColor, QAction
from PyQt6.QtCore import Qt, QDate

class Database:
    def __init__(self, db_name="devices.db"):
        """Khởi tạo kết nối với cơ sở dữ liệu"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Kết nối đến cơ sở dữ liệu"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Đã kết nối tới {self.db_name}")
        except sqlite3.Error as e:
            print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
            
    def create_tables(self):
        """Tạo bảng nếu chưa tồn tại"""
        try:
            # Bảng devices để lưu thông tin thiết bị
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hwid TEXT UNIQUE NOT NULL,
                device_name TEXT,
                user_name TEXT,
                email TEXT,
                activation_date TEXT,
                expiry_date TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Bảng activation_history để lưu lịch sử kích hoạt
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hwid TEXT,
                activation_date TEXT,
                ip_address TEXT,
                status TEXT,
                FOREIGN KEY (hwid) REFERENCES devices (hwid)
            )
            ''')
            
            self.conn.commit()
            print("Bảng dữ liệu đã được tạo")
        except sqlite3.Error as e:
            print(f"Lỗi tạo bảng: {e}")
    
    def add_device(self, hwid, device_name="", user_name="", email="", 
                  activation_date=None, expiry_date=None, status="active", notes=""):
        """Thêm thiết bị mới vào cơ sở dữ liệu"""
        try:
            # Kiểm tra xem HWID đã tồn tại chưa
            self.cursor.execute("SELECT hwid FROM devices WHERE hwid=?", (hwid,))
            if self.cursor.fetchone():
                return False, "HWID đã tồn tại trong hệ thống"
            
            # Nếu không cung cấp ngày, sử dụng ngày hiện tại
            if not activation_date:
                activation_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Thêm thiết bị mới
            self.cursor.execute('''
            INSERT INTO devices (hwid, device_name, user_name, email, 
                               activation_date, expiry_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hwid, device_name, user_name, email, activation_date, 
                 expiry_date, status, notes))
            
            self.conn.commit()
            return True, "Thiết bị đã được thêm thành công"
        except sqlite3.Error as e:
            return False, f"Lỗi khi thêm thiết bị: {e}"
    
    def update_device(self, hwid, device_name=None, user_name=None, email=None, 
                     activation_date=None, expiry_date=None, status=None, notes=None):
        """Cập nhật thông tin thiết bị"""
        try:
            # Xây dựng câu lệnh cập nhật động
            update_fields = []
            values = []
            
            if device_name is not None:
                update_fields.append("device_name = ?")
                values.append(device_name)
            if user_name is not None:
                update_fields.append("user_name = ?")
                values.append(user_name)
            if email is not None:
                update_fields.append("email = ?")
                values.append(email)
            if activation_date is not None:
                update_fields.append("activation_date = ?")
                values.append(activation_date)
            if expiry_date is not None:
                update_fields.append("expiry_date = ?")
                values.append(expiry_date)
            if status is not None:
                update_fields.append("status = ?")
                values.append(status)
            if notes is not None:
                update_fields.append("notes = ?")
                values.append(notes)
            
            if not update_fields:
                return False, "Không có thông tin nào để cập nhật"
            
            # Thêm HWID vào danh sách giá trị
            values.append(hwid)
            
            # Thực hiện cập nhật
            query = f"UPDATE devices SET {', '.join(update_fields)} WHERE hwid = ?"
            self.cursor.execute(query, values)
            
            if self.cursor.rowcount == 0:
                return False, "Không tìm thấy thiết bị với HWID này"
            
            self.conn.commit()
            return True, "Thông tin thiết bị đã được cập nhật"
        except sqlite3.Error as e:
            return False, f"Lỗi khi cập nhật thiết bị: {e}"
    
    def delete_device(self, hwid):
        """Xóa thiết bị khỏi cơ sở dữ liệu"""
        try:
            self.cursor.execute("DELETE FROM devices WHERE hwid = ?", (hwid,))
            
            if self.cursor.rowcount == 0:
                return False, "Không tìm thấy thiết bị với HWID này"
            
            # Xóa lịch sử kích hoạt liên quan
            self.cursor.execute("DELETE FROM activation_history WHERE hwid = ?", (hwid,))
            
            self.conn.commit()
            return True, "Thiết bị đã được xóa thành công"
        except sqlite3.Error as e:
            return False, f"Lỗi khi xóa thiết bị: {e}"
    
    def get_all_devices(self):
        """Lấy danh sách tất cả thiết bị"""
        try:
            self.cursor.execute('''
            SELECT id, hwid, device_name, user_name, email, 
                   activation_date, expiry_date, status, notes 
            FROM devices ORDER BY id DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy danh sách thiết bị: {e}")
            return []
    
    def search_devices(self, keyword):
        """Tìm kiếm thiết bị theo từ khóa"""
        try:
            keyword = f"%{keyword}%"
            self.cursor.execute('''
            SELECT id, hwid, device_name, user_name, email, 
                   activation_date, expiry_date, status, notes 
            FROM devices 
            WHERE hwid LIKE ? OR device_name LIKE ? OR user_name LIKE ? 
                  OR email LIKE ? OR notes LIKE ?
            ORDER BY id DESC
            ''', (keyword, keyword, keyword, keyword, keyword))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi khi tìm kiếm thiết bị: {e}")
            return []
    
    def check_device(self, hwid):
        """Kiểm tra xem thiết bị có được kích hoạt và còn hạn sử dụng không"""
        try:
            self.cursor.execute('''
            SELECT status, expiry_date FROM devices WHERE hwid = ?
            ''', (hwid,))
            result = self.cursor.fetchone()
            
            if not result:
                return False, "Thiết bị chưa được kích hoạt"
            
            status, expiry_date = result
            
            if status != "active":
                return False, f"Thiết bị đã bị {status}"
            
            if expiry_date:
                try:
                    expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
                    if expiry < datetime.datetime.now():
                        return False, "Thiết bị đã hết hạn sử dụng"
                except ValueError:
                    pass  # Bỏ qua lỗi định dạng ngày
            
            # Ghi lại lịch sử kích hoạt
            self.log_activation(hwid, "success")
            
            return True, "Thiết bị hợp lệ"
        except sqlite3.Error as e:
            return False, f"Lỗi khi kiểm tra thiết bị: {e}"
    
    def log_activation(self, hwid, status, ip_address=""):
        """Ghi lại lịch sử kích hoạt"""
        try:
            activation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
            INSERT INTO activation_history (hwid, activation_date, ip_address, status)
            VALUES (?, ?, ?, ?)
            ''', (hwid, activation_date, ip_address, status))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Lỗi khi ghi lịch sử kích hoạt: {e}")
    
    def get_activation_history(self, hwid=None):
        """Lấy lịch sử kích hoạt của một hoặc tất cả thiết bị"""
        try:
            if hwid:
                self.cursor.execute('''
                SELECT id, hwid, activation_date, ip_address, status 
                FROM activation_history 
                WHERE hwid = ? ORDER BY activation_date DESC
                ''', (hwid,))
            else:
                self.cursor.execute('''
                SELECT id, hwid, activation_date, ip_address, status 
                FROM activation_history 
                ORDER BY activation_date DESC
                ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Lỗi khi lấy lịch sử kích hoạt: {e}")
            return []
    
    def close(self):
        """Đóng kết nối cơ sở dữ liệu"""
        if self.conn:
            self.conn.close()
            print("Đã đóng kết nối cơ sở dữ liệu")

class DeviceDialog(QDialog):
    def __init__(self, parent=None, device_data=None):
        """Dialog để thêm hoặc sửa thông tin thiết bị"""
        super().__init__(parent)
        self.device_data = device_data  # None nếu thêm mới, có dữ liệu nếu sửa
        self.setWindowTitle("Thêm thiết bị mới" if not device_data else "Sửa thông tin thiết bị")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # HWID
        self.hwid_edit = QLineEdit(self)
        if self.device_data:
            self.hwid_edit.setText(self.device_data[1])  # hwid ở vị trí thứ 2
            self.hwid_edit.setReadOnly(True)  # Không cho phép sửa HWID
        layout.addRow("HWID:", self.hwid_edit)
        
        # Tên thiết bị
        self.device_name_edit = QLineEdit(self)
        if self.device_data:
            self.device_name_edit.setText(self.device_data[2])
        layout.addRow("Tên thiết bị:", self.device_name_edit)
        
        # Tên người dùng
        self.user_name_edit = QLineEdit(self)
        if self.device_data:
            self.user_name_edit.setText(self.device_data[3])
        layout.addRow("Tên người dùng:", self.user_name_edit)
        
        # Email
        self.email_edit = QLineEdit(self)
        if self.device_data:
            self.email_edit.setText(self.device_data[4])
        layout.addRow("Email:", self.email_edit)
        
        # Ngày kích hoạt
        self.activation_date_edit = QDateEdit(self)
        self.activation_date_edit.setCalendarPopup(True)
        self.activation_date_edit.setDate(QDate.currentDate())
        if self.device_data and self.device_data[5]:
            try:
                date = QDate.fromString(self.device_data[5], "yyyy-MM-dd")
                self.activation_date_edit.setDate(date)
            except:
                pass
        layout.addRow("Ngày kích hoạt:", self.activation_date_edit)
        
        # Ngày hết hạn
        self.expiry_date_edit = QDateEdit(self)
        self.expiry_date_edit.setCalendarPopup(True)
        # Mặc định là 1 năm sau
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        if self.device_data and self.device_data[6]:
            try:
                date = QDate.fromString(self.device_data[6], "yyyy-MM-dd")
                self.expiry_date_edit.setDate(date)
            except:
                pass
        layout.addRow("Ngày hết hạn:", self.expiry_date_edit)
        
        # Trạng thái
        self.status_edit = QLineEdit(self)
        self.status_edit.setText("active")
        if self.device_data:
            self.status_edit.setText(self.device_data[7])
        layout.addRow("Trạng thái:", self.status_edit)
        
        # Ghi chú
        self.notes_edit = QLineEdit(self)
        if self.device_data and self.device_data[8]:
            self.notes_edit.setText(self.device_data[8])
        layout.addRow("Ghi chú:", self.notes_edit)
        
        # Nút Lưu và Hủy
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Lưu", self)
        self.save_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Hủy", self)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addRow("", button_layout)
    
    def get_data(self):
        """Lấy dữ liệu từ form"""
        return {
            "hwid": self.hwid_edit.text(),
            "device_name": self.device_name_edit.text(),
            "user_name": self.user_name_edit.text(),
            "email": self.email_edit.text(),
            "activation_date": self.activation_date_edit.date().toString("yyyy-MM-dd"),
            "expiry_date": self.expiry_date_edit.date().toString("yyyy-MM-dd"),
            "status": self.status_edit.text(),
            "notes": self.notes_edit.text()
        }

class DeviceManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Quản lý thiết bị")
        self.setGeometry(100, 100, 1000, 600)
        
        # Thanh công cụ
        toolbar = self.addToolBar("Công cụ")
        
        # Nút Thêm thiết bị
        add_action = QAction("Thêm thiết bị", self)
        add_action.triggered.connect(self.add_device)
        toolbar.addAction(add_action)
        
        # Nút Sửa thiết bị
        edit_action = QAction("Sửa thiết bị", self)
        edit_action.triggered.connect(self.edit_device)
        toolbar.addAction(edit_action)
        
        # Nút Xóa thiết bị
        delete_action = QAction("Xóa thiết bị", self)
        delete_action.triggered.connect(self.delete_device)
        toolbar.addAction(delete_action)
        
        # Nút Làm mới
        refresh_action = QAction("Làm mới", self)
        refresh_action.triggered.connect(self.load_devices)
        toolbar.addAction(refresh_action)
        
        # Widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout chính
        main_layout = QVBoxLayout(central_widget)
        
        # Thanh tìm kiếm
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tìm kiếm thiết bị...")
        self.search_edit.returnPressed.connect(self.search_devices)
        
        search_button = QPushButton("Tìm kiếm")
        search_button.clicked.connect(self.search_devices)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(search_button)
        
        main_layout.addLayout(search_layout)
        
        # Bảng thiết bị
        self.device_table = QTableWidget()
        self.device_table.setColumnCount(9)
        self.device_table.setHorizontalHeaderLabels([
            "ID", "HWID", "Tên thiết bị", "Người dùng", "Email", 
            "Ngày kích hoạt", "Ngày hết hạn", "Trạng thái", "Ghi chú"
        ])
        
        # Thiết lập độ rộng cột
        header = self.device_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Tên thiết bị
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Stretch)  # Ghi chú
        
        main_layout.addWidget(self.device_table)
        
        # Hiển thị thiết bị
        self.load_devices()
        
    def load_devices(self):
        """Tải danh sách thiết bị từ cơ sở dữ liệu"""
        devices = self.db.get_all_devices()
        self.update_table(devices)
    
    def update_table(self, devices):
        """Cập nhật bảng với dữ liệu mới"""
        self.device_table.setRowCount(0)  # Xóa tất cả dòng
        
        for row, device in enumerate(devices):
            self.device_table.insertRow(row)
            
            for col, value in enumerate(device):
                item = QTableWidgetItem(str(value) if value is not None else "")
                
                # Đổi màu cho trạng thái
                if col == 7:  # Cột trạng thái
                    if value == "active":
                        item.setForeground(QColor(0, 128, 0))  # Xanh lá
                    elif value == "blocked":
                        item.setForeground(QColor(255, 0, 0))  # Đỏ
                    elif value == "expired":
                        item.setForeground(QColor(255, 165, 0))  # Cam
                
                self.device_table.setItem(row, col, item)
    
    def add_device(self):
        """Thêm thiết bị mới"""
        dialog = DeviceDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            success, message = self.db.add_device(
                hwid=data["hwid"],
                device_name=data["device_name"],
                user_name=data["user_name"],
                email=data["email"],
                activation_date=data["activation_date"],
                expiry_date=data["expiry_date"],
                status=data["status"],
                notes=data["notes"]
            )
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_devices()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def edit_device(self):
        """Sửa thông tin thiết bị"""
        selected_rows = self.device_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thiết bị để sửa")
            return
        
        row = selected_rows[0].row()
        device_data = []
        for col in range(self.device_table.columnCount()):
            device_data.append(self.device_table.item(row, col).text())
        
        dialog = DeviceDialog(self, device_data)
        if dialog.exec():
            data = dialog.get_data()
            success, message = self.db.update_device(
                hwid=data["hwid"],
                device_name=data["device_name"],
                user_name=data["user_name"],
                email=data["email"],
                activation_date=data["activation_date"],
                expiry_date=data["expiry_date"],
                status=data["status"],
                notes=data["notes"]
            )
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_devices()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def delete_device(self):
        """Xóa thiết bị"""
        selected_rows = self.device_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thiết bị để xóa")
            return
        
        row = selected_rows[0].row()
        hwid = self.device_table.item(row, 1).text()  # HWID ở cột thứ 2
        
        reply = QMessageBox.question(
            self, "Xác nhận xóa", 
            f"Bạn có chắc chắn muốn xóa thiết bị có HWID: {hwid}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.db.delete_device(hwid)
            
            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_devices()
            else:
                QMessageBox.warning(self, "Lỗi", message)
    
    def search_devices(self):
        """Tìm kiếm thiết bị"""
        keyword = self.search_edit.text()
        if not keyword:
            self.load_devices()
            return
        
        devices = self.db.search_devices(keyword)
        self.update_table(devices)
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        self.db.close()
        event.accept()

# Kết nối với cửa sổ đăng nhập - cần import vào login_form.py
def check_device_in_db(hwid):
    """Kiểm tra xem thiết bị có trong cơ sở dữ liệu và còn hạn sử dụng không"""
    db = Database()
    success, message = db.check_device(hwid)
    db.close()
    return success, message

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeviceManager()
    window.show()
    sys.exit(app.exec()) 