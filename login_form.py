import sys
import os
import getpass 
import uuid
import hashlib
import webbrowser
import socket
import urllib.parse
import urllib.request
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy, 
                             QMessageBox)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor, QPalette, QClipboard
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, QAbstractAnimation, QVariantAnimation

# Import hàm kiểm tra thiết bị từ manage_device
try:
    from manage_device import check_device_in_db
except ImportError:
    # Fallback nếu không import được
    def check_device_in_db(hwid):
        # Luôn trả về True để tạm thời bỏ qua kiểm tra
        print("Không thể import module manage_device, bỏ qua kiểm tra HWID")
        return True, "Thiết bị hợp lệ (chế độ phát triển)"

# Lấy đường dẫn tuyệt đối của thư mục gốc ứng dụng
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

class TypingLabel(QLabel):
    def __init__(self, full_text="", parent=None):
        super().__init__("", parent) # Khởi tạo với text rỗng
        self._full_text = full_text
        self._current_text = ""
        self._char_index = 0
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._type_char)
        self.animation_delay_ms = 50 # Tốc độ gõ chữ (ms per char)
        self._on_complete_callback = None  # Callback khi hoàn thành typing
        self._color_change_index = -1  # Vị trí bắt đầu thay đổi màu
        self._highlight_color = "#FFBF3F"  # Màu highlight

    def set_full_text(self, text):
        self._full_text = text
        self._current_text = ""
        self._char_index = 0
        self.setText("") # Xóa text hiện tại trước khi bắt đầu animation mới

    def set_color_change_at(self, index, highlight_color="#FFBF3F"):
        """Thiết lập vị trí bắt đầu thay đổi màu và màu highlight"""
        self._color_change_index = index
        self._highlight_color = highlight_color

    def set_on_complete_callback(self, callback):
        """Thiết lập callback function sẽ được gọi khi typing hoàn thành"""
        self._on_complete_callback = callback

    def start_typing(self, delay_start_ms=0):
        if not self._full_text:
            self.setText("") # Nếu không có text thì hiển thị rỗng
            return
        # Đảm bảo reset trước khi bắt đầu
        self._current_text = ""
        self._char_index = 0
        self.setText("")

        if delay_start_ms > 0:
            QTimer.singleShot(delay_start_ms, self._start_actual_typing)
        else:
            self._start_actual_typing()

    def _start_actual_typing(self):
        if self._full_text: # Chỉ bắt đầu nếu có text
            self._typing_timer.start(self.animation_delay_ms)

    def _type_char(self):
        if self._char_index < len(self._full_text):
            self._current_text += self._full_text[self._char_index]
            
            # Nếu có thiết lập thay đổi màu và đã đến vị trí đó
            if self._color_change_index >= 0 and self._char_index >= self._color_change_index:
                # Tạo HTML với phần đầu màu bình thường và phần sau màu highlight
                normal_part = self._current_text[:self._color_change_index]
                highlight_part = self._current_text[self._color_change_index:]
                html_text = f'{normal_part}<span style="color: {self._highlight_color};">{highlight_part}</span>'
                self.setText(html_text)
            else:
                self.setText(self._current_text)
            
            self._char_index += 1
        else:
            self._typing_timer.stop()
            # Gọi callback nếu có
            if self._on_complete_callback:
                self._on_complete_callback()

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #2D2D2D; border-bottom: 1px solid #444444;")
        
        # Layout cho title bar
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(8)
        
        # Các nút macOS style
        self.close_btn = QPushButton()
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        
        # Thiết lập style cho các nút
        button_style = """
            QPushButton {
                border-radius: 6px;
                width: 12px;
                height: 12px;
                border: none;
            }
            QPushButton:hover {
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        """
        
        # Nút đóng (đỏ)
        self.close_btn.setStyleSheet(button_style + "QPushButton { background-color: #FF5F57; }")
        self.close_btn.setFixedSize(12, 12)
        self.close_btn.clicked.connect(self.close_window)
        
        # Nút thu nhỏ (vàng)
        self.minimize_btn.setStyleSheet(button_style + "QPushButton { background-color: #FFBD2E; }")
        self.minimize_btn.setFixedSize(12, 12)
        self.minimize_btn.clicked.connect(self.minimize_window)
        
        # Nút phóng to (xanh lá)
        self.maximize_btn.setStyleSheet(button_style + "QPushButton { background-color: #28CA42; }")
        self.maximize_btn.setFixedSize(12, 12)
        self.maximize_btn.clicked.connect(self.maximize_window)
        
        # Title
        self.title_label = QLabel("VTN VIP - ĐĂNG NHẬP HỆ THỐNG")
        self.title_label.setStyleSheet("color: #E0E0E0; font-weight: bold; font-size: 14px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Thêm vào layout
        layout.addWidget(self.close_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        # Biến để theo dõi việc kéo cửa sổ
        self.dragging = False
        self.drag_position = None
    
    def close_window(self):
        if self.parent:
            self.parent.close()
    
    def minimize_window(self):
        if self.parent:
            self.parent.showMinimized()
    
    def maximize_window(self):
        if self.parent:
            if self.parent.isMaximized():
                self.parent.showNormal()
            else:
                self.parent.showMaximized()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_position:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.drag_position = None

# Hàm lấy HWID của máy
def get_hwid():
    """Lấy Hardware ID duy nhất cho máy tính"""
    try:
        # Kết hợp thông tin phần cứng để tạo ID duy nhất
        mac = uuid.getnode()
        computer_name = os.getenv('COMPUTERNAME', '') or os.uname().nodename
        username = getpass.getuser()
        
        # Tạo chuỗi từ các thông tin thu thập được
        combined = f"{mac}-{computer_name}-{username}"
        
        # Tạo mã hash từ chuỗi thông tin
        hwid = hashlib.md5(combined.encode()).hexdigest().upper()
        
        # Lấy 10 ký tự đầu tiên của mã hash
        return hwid[:10]
    except:
        # Fallback nếu có lỗi
        return hashlib.md5(str(uuid.getnode()).encode()).hexdigest().upper()[:10]

# Hàm tạo file HTML cho việc kích hoạt
def create_activation_html(hwid, output_path="activation.html"):
    """Tạo file HTML để người dùng có thể kích hoạt mã máy"""
    # Kiểm tra xem chúng ta có thể kết nối đến máy chủ kích hoạt không
    try:
        # Lấy địa chỉ IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Thử kết nối đến máy chủ kích hoạt (port 8000)
        activation_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        activation_server.settimeout(1)  # Đặt timeout 1 giây
        result = activation_server.connect_ex((local_ip, 8000))
        activation_server.close()
        
        if result == 0:
            # Máy chủ kích hoạt đang chạy, điều hướng đến đó
            url = f"http://{local_ip}:8000/?hwid={urllib.parse.quote(hwid)}"
            webbrowser.open(url)
            return None
    except:
        pass  # Bỏ qua lỗi và sử dụng HTML tĩnh
    
    # Sử dụng HTML tĩnh nếu không kết nối được máy chủ
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kích hoạt key VTN VIP</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: rgba(0, 0, 0, 0.5);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            width: 400px;
            text-align: center;
            padding: 20px;
        }}
        .info-icon {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: rgba(33, 150, 243, 0.1);
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0 auto 20px auto;
            font-size: 36px;
            color: #2196F3;
        }}
        h1 {{
            color: #333;
            font-size: 24px;
            margin-bottom: 15px;
        }}
        p {{
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        input {{
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            box-sizing: border-box;
            font-size: 14px;
        }}
        .button-container {{
            display: flex;
            justify-content: center;
            gap: 10px;
        }}
        button {{
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
        }}
        .activate-btn {{
            background-color: #2196F3;
            color: white;
        }}
        .cancel-btn {{
            background-color: #ff7675;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="info-icon">i</div>
        <h1>Kích hoạt key</h1>
        <p>Sao chép mã máy trong tool và dán vào ô dưới</p>
        <input type="text" id="hwid-input" placeholder="Nhập mã máy của bạn" value="{hwid}" readonly>
        <div class="button-container">
            <button class="activate-btn" onclick="activateKey()">Kích hoạt</button>
            <button class="cancel-btn" onclick="window.close()">Huỷ</button>
        </div>
    </div>
    
    <script>
        function activateKey() {{
            // Giả lập kích hoạt thành công
            alert('Vui lòng liên hệ quản trị viên để kích hoạt mã máy này.');
            // Có thể mở một hướng dẫn về cách liên hệ admin ở đây
            // window.location.href = "https://example.com/contact";
        }}
        
        // Tự động chọn mã máy khi trang được tải
        window.onload = function() {{
            document.getElementById('hwid-input').select();
        }}
    </script>
</body>
</html>
"""
    # Ghi nội dung HTML vào file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Lấy HWID của máy
        self.hwid = get_hwid()
        self.is_activated = False
        # Biến để theo dõi trạng thái đăng nhập thành công
        self.login_confirmed = False
        # Hàm callback sẽ được gọi khi đăng nhập thành công
        self.login_confirmed_signal = None
        
        self.pc_name = ""
        try:
            # Ưu tiên getpass.getuser() vì nó đáng tin cậy hơn trên nhiều nền tảng
            self.pc_name = getpass.getuser().upper()
        except Exception:
            try:
                # Fallback nếu getpass không hoạt động
                self.pc_name = os.getlogin().upper()
            except Exception:
                self.pc_name = "USER" # Giá trị mặc định nếu không lấy được

        # Thiết lập opacity là 0 cho hiệu ứng fade in
        self.setWindowOpacity(0.0)
        
        self.init_ui()
        
        # Chạy hiệu ứng fade in khi cửa sổ hiển thị
        QTimer.singleShot(100, self.fadeIn)
        
        # Kiểm tra thiết bị đã kích hoạt chưa
        QTimer.singleShot(1000, self.check_activation)
        
        # Chạy hiệu ứng animations sau khi kiểm tra kích hoạt
        QTimer.singleShot(1500, self.start_animations)

    def init_ui(self):
        # Loại bỏ title bar mặc định và thiết lập cửa sổ
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(800, 450) # Kích thước cửa sổ
        self.setStyleSheet("background-color: #2D2D2D;") # Màu nền chính

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # Không có lề cho layout chính
        main_layout.setSpacing(0)

        # --- Custom Title Bar ---
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)

        # --- Content Layout ---
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # --- Left Panel (Logo) ---
        left_panel = QWidget()
        left_panel.setFixedWidth(300) # Chiều rộng cố định cho panel logo
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(20, 20, 20, 20)
        left_panel.setStyleSheet("background-color: #1E1E1E;") # Màu nền panel logo

        self.logo_label = QLabel()
        logo_path = os.path.join(APP_ROOT, "imgs", "vtn_vip.png")
        logo_pixmap = QPixmap(logo_path) # Sử dụng đường dẫn tuyệt đối
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.logo_label.setText("LOGO") # Placeholder nếu không có ảnh
            self.logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
            self.logo_label.setStyleSheet("color: #FFD700;")

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel_layout.addStretch(1)
        left_panel_layout.addWidget(self.logo_label)
        left_panel_layout.addStretch(1)

        # --- Vertical Separator ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #444444;") # Màu của đường kẻ

        # --- Right Panel (Login Info) ---
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(40, 20, 40, 40) # Lề cho panel phải
        right_panel_layout.setSpacing(15)

        # "XIN CHÀO" text
        self.welcome_text_label = TypingLabel()
        welcome_font = QFont("Roboto", 20, QFont.Weight.Bold)
        self.welcome_text_label.setFont(welcome_font)
        self.welcome_text_label.setStyleSheet("color: #E0E0E0;")
        self.welcome_text_label.setTextFormat(Qt.TextFormat.RichText)  # Cho phép hiển thị HTML

        # "VUI LÒNG KÍCH HOẠT" text
        self.instruction_text_label = TypingLabel()
        instruction_font = QFont("Roboto", 11)
        self.instruction_text_label.setFont(instruction_font)
        self.instruction_text_label.setStyleSheet("color: #A0A0A0;")

        # Mã kích hoạt (HWID)
        self.code_label = TypingLabel()
        code_font = QFont("Roboto", 22, QFont.Weight.Bold)
        self.code_label.setFont(code_font)
        self.code_label.setStyleSheet("color: #FFBF3F; margin-top: 20px; margin-bottom: 20px;") # Màu vàng cam
        self.code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Thêm label hiển thị thông tin hết hạn
        self.expiry_label = QLabel()
        expiry_font = QFont("Roboto", 12)
        self.expiry_label.setFont(expiry_font)
        self.expiry_label.setStyleSheet("color: #4CAF50; margin-top: 5px;")
        self.expiry_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.expiry_label.setVisible(False)  # Ẩn ban đầu
        
        # Nút sao chép mã
        self.copy_button = QPushButton("SAO CHÉP MÃ")
        copy_button_font = QFont("Roboto", 10)
        self.copy_button.setFont(copy_button_font)
        self.copy_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: #444444;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)
        self.copy_button.setMaximumWidth(200)
        self.copy_button.clicked.connect(self.copy_hwid_to_clipboard)
        
        # Nút kích hoạt
        self.activate_button = QPushButton("MỞ TRANG KÍCH HOẠT")
        activate_button_font = QFont("Roboto", 10)
        self.activate_button.setFont(activate_button_font)
        self.activate_button.setStyleSheet("""
            QPushButton {
                color: #FFFFFF;
                background-color: #2196F3;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        self.activate_button.setMaximumWidth(200)
        self.activate_button.clicked.connect(self.open_activation_page)

        # Nút Đăng nhập
        self.login_button = QPushButton(" ĐĂNG NHẬP")
        login_button_font = QFont("Roboto", 12, QFont.Weight.Bold)
        self.login_button.setFont(login_button_font)
        self.login_button.setMinimumHeight(50)
        
        # Mặc định nút đăng nhập sẽ bị vô hiệu hóa cho đến khi kiểm tra kích hoạt
        self.login_button.setEnabled(False)
        
        self.login_button.setStyleSheet("""
            QPushButton {
                color: #AAAAAA;
                background-color: #383838;
                border: 2px solid #555555;
                border-radius: 25px; /* Bo tròn góc */
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #484848;
            }
        """)
        
        # Icon cho nút (nếu có)
        try:
            icon_path = os.path.join(APP_ROOT, "assets", "icons", "fingerprint-alt-svgrepo-com.svg")
            fingerprint_icon = QIcon(icon_path)
            if not fingerprint_icon.isNull():
                self.login_button.setIcon(fingerprint_icon)
                self.login_button.setIconSize(self.login_button.sizeHint() / 2.5) # Điều chỉnh kích thước icon
        except Exception as e:
            print(f"Không thể tải icon đăng nhập: {e}")

        # Tạo layout cho nút sao chép và kích hoạt
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.activate_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Thêm widgets vào right_panel_layout
        right_panel_layout.addStretch(1) # Đẩy nội dung xuống giữa một chút
        right_panel_layout.addWidget(self.welcome_text_label)
        right_panel_layout.addWidget(self.instruction_text_label)
        right_panel_layout.addWidget(self.code_label)
        right_panel_layout.addWidget(self.expiry_label)  # Thêm label hết hạn
        right_panel_layout.addLayout(button_layout)
        right_panel_layout.addSpacing(20) # Thêm khoảng trống trước nút
        right_panel_layout.addWidget(self.login_button)
        right_panel_layout.addStretch(2) # Đẩy nội dung lên trên một chút

        # Thêm panels vào content_layout
        content_layout.addWidget(left_panel)
        content_layout.addWidget(separator)
        content_layout.addWidget(right_panel, 1) # Cho panel phải chiếm phần còn lại

        main_layout.addWidget(content_widget)

        self.setLayout(main_layout)

        # Kết nối sự kiện
        self.login_button.clicked.connect(self.on_login_clicked)

    def start_animations(self):
        # Thiết lập nội dung text cho các label có hiệu ứng với tên máy là màu #FFBF3F (chỉ tên máy mới có màu)
        welcome_text = f"XIN CHÀO, {self.pc_name}"
        self.welcome_text_label.set_full_text(welcome_text)
        self.welcome_text_label.setStyleSheet("color: #E0E0E0;")  # Màu trắng cho phần còn lại
        
        # Tính vị trí bắt đầu của tên máy (sau "XIN CHÀO, ")
        color_change_position = len("XIN CHÀO, ")
        self.welcome_text_label.set_color_change_at(color_change_position, "#FFBF3F")

        # Thiết lập text cho instruction_text_label chỉ khi thiết bị chưa được kích hoạt
        # (đối với thiết bị đã kích hoạt, text sẽ được thiết lập trong phương thức kiểm tra kích hoạt)
        if not self.is_activated:
            self.instruction_text_label.set_full_text("VUI LÒNG KÍCH HOẠT MÃ MÁY ĐỂ SỬ DỤNG")
        
        # Hiển thị mã máy (HWID)
        self.code_label.setText(self.hwid)
        self.code_label.setStyleSheet("color: #FFBF3F; margin-top: 20px; margin-bottom: 20px;") # Màu vàng cam

        # Bắt đầu hiệu ứng gõ chữ lần lượt
        # Mỗi label bắt đầu sau khi label trước đó có thể đã hoàn thành một phần
        # (tính toán dựa trên độ dài text và tốc độ gõ)
        delay_increment = self.welcome_text_label.animation_delay_ms * len(self.welcome_text_label._full_text) // 2
        
        self.welcome_text_label.start_typing(delay_start_ms=100) # Giảm delay xuống 100ms
        
        # Tính toán delay cho instruction_text_label và chỉ bắt đầu gõ nếu có text
        if self.instruction_text_label._full_text:
            delay_instruction = 100 + self.welcome_text_label.animation_delay_ms * len(self.welcome_text_label._full_text) + 200 # Thêm 200ms nghỉ
            self.instruction_text_label.start_typing(delay_start_ms=delay_instruction)

    def fadeIn(self):
        """Tạo hiệu ứng fade in khi hiển thị cửa sổ"""
        self.fade_animation = QVariantAnimation()
        self.fade_animation.setDuration(600)  # Thời gian hiệu ứng (ms)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.fade_animation.valueChanged.connect(self.setWindowOpacity)
        self.fade_animation.start()

    def copy_hwid_to_clipboard(self):
        """Sao chép HWID vào clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.hwid)
        # Có thể thêm thông báo nhỏ để xác nhận đã sao chép
        self.code_label.setStyleSheet("color: #4CAF50; margin-top: 20px; margin-bottom: 20px;") # Đổi màu sang xanh lá
        QTimer.singleShot(1000, lambda: self.code_label.setStyleSheet("color: #FFBF3F; margin-top: 20px; margin-bottom: 20px;")) # Đổi lại màu sau 1s
    
    def open_activation_page(self):
        """Mở trang kích hoạt"""
        # Tạo file HTML kích hoạt
        activation_file = create_activation_html(self.hwid)
        
        # Nếu create_activation_html trả về None, nghĩa là đã mở trang máy chủ
        if activation_file:
            # Mở file bằng trình duyệt mặc định
            webbrowser.open(f'file://{os.path.abspath(activation_file)}')
    
    def check_activation(self):
        """Kiểm tra xem thiết bị đã được kích hoạt chưa"""
        try:
            # Thử kiểm tra với máy chủ kích hoạt trước
            self.check_activation_with_server()
        except Exception as e:
            print(f"Không thể kết nối đến máy chủ kích hoạt: {e}")
            # Fallback: Kiểm tra với cơ sở dữ liệu cục bộ
            self.check_activation_with_local_db()

    def check_activation_with_server(self):
        """Kiểm tra kích hoạt thông qua máy chủ kích hoạt"""
        # Lấy địa chỉ IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # URL của API kiểm tra kích hoạt
        activation_url = f"http://{local_ip}:8000/list-activated"
        
        # Tạo dữ liệu JSON để gửi
        data = json.dumps({"hwid": self.hwid}).encode('utf-8')
        
        # Tạo request
        req = urllib.request.Request(
            activation_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # Gửi request và nhận phản hồi
        with urllib.request.urlopen(req, timeout=2) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        # Xử lý kết quả
        if result.get('success', False) and result.get('activated', False):
            self.is_activated = True
            
            # Lấy thông tin thiết bị
            device_info = result.get('device_info', {})
            expiry_message = device_info.get('expiry_message', '')
            
            # Cập nhật giao diện
            self.instruction_text_label.set_full_text("THIẾT BỊ ĐÃ ĐƯỢC KÍCH HOẠT")
            self.instruction_text_label.setStyleSheet("color: #4CAF50;")  # Màu xanh lá
            
            # Hiển thị HWID và thông tin hết hạn riêng biệt
            if expiry_message:
                # Hiển thị HWID trong code_label
                self.code_label.setText(self.hwid)
                self.code_label.setStyleSheet("color: #4CAF50; margin-top: 10px; margin-bottom: 5px;")
                
                # Hiển thị thông tin hết hạn trong expiry_label
                self.expiry_label.setText(expiry_message)
                self.expiry_label.setVisible(True)
                
                # Đặt màu dựa trên số ngày còn lại
                if "đã hết hạn" in expiry_message:
                    self.expiry_label.setStyleSheet("color: #FF5722; margin-top: 5px;")  # Màu cam đỏ cho hết hạn
                elif "Hết hạn hôm nay" in expiry_message or "Còn 1 ngày" in expiry_message:
                    self.expiry_label.setStyleSheet("color: #FFC107; margin-top: 5px;")  # Màu vàng cảnh báo
                else:
                    self.expiry_label.setStyleSheet("color: #4CAF50; margin-top: 5px;")  # Màu xanh lá bình thường
            else:
                # Nếu không có thông tin hết hạn, chỉ hiển thị HWID
                self.code_label.setText(self.hwid)
                self.code_label.setStyleSheet("color: #4CAF50; margin-top: 20px; margin-bottom: 20px;")
                self.expiry_label.setVisible(False)
            
            # Ẩn nút kích hoạt và sao chép, hiển thị nút đăng nhập
            self.copy_button.setVisible(False)
            self.activate_button.setVisible(False)
            self.login_button.setEnabled(True)
            self.login_button.setText(" ĐĂNG NHẬP")
            
            # Đặt icon cho nút đăng nhập
            try:
                icon_path = os.path.join(APP_ROOT, "assets", "icons", "fingerprint-alt-svgrepo-com.svg")
                fingerprint_icon = QIcon(icon_path)
                if not fingerprint_icon.isNull():
                    self.login_button.setIcon(fingerprint_icon)
                    self.login_button.setIconSize(self.login_button.sizeHint() / 2.5)
            except Exception as e:
                print(f"Không thể tải icon đăng nhập: {e}")
                
            self.login_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #4CAF50;
                    border: none;
                    border-radius: 25px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b3d;
                }
            """)
        else:
            self.is_activated = False
            # Cập nhật giao diện khi thiết bị chưa kích hoạt
            error_message = result.get('message', 'Thiết bị chưa được kích hoạt')
            self.instruction_text_label.set_full_text(error_message)
            self.instruction_text_label.setStyleSheet("color: #FF5722;")  # Màu cam đỏ
            
            self.login_button.setEnabled(False)
            self.login_button.setStyleSheet("""
                QPushButton {
                    color: #AAAAAA;
                    background-color: #383838;
                    border: 2px solid #555555;
                    border-radius: 25px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #383838;
                }
            """)

    def check_activation_with_local_db(self):
        """Kiểm tra kích hoạt bằng cơ sở dữ liệu cục bộ"""
        try:
            # Import hàm check_device_in_db từ manage_device
            from manage_device import check_device_in_db
            success, message = check_device_in_db(self.hwid)
            
            if success:
                self.is_activated = True
                # Cập nhật giao diện khi thiết bị đã kích hoạt
                self.instruction_text_label.set_full_text("THIẾT BỊ ĐÃ ĐƯỢC KÍCH HOẠT")
                self.instruction_text_label.setStyleSheet("color: #4CAF50;")  # Màu xanh lá
                
                # Kiểm tra xem message có chứa thông tin hết hạn không
                if "hết hạn ngày" in message or "ngày sử dụng" in message:
                    # Hiển thị HWID trong code_label
                    self.code_label.setText(self.hwid)
                    self.code_label.setStyleSheet("color: #4CAF50; margin-top: 10px; margin-bottom: 5px;")
                    
                    # Hiển thị thông tin hết hạn trong expiry_label
                    self.expiry_label.setText(message)
                    self.expiry_label.setVisible(True)
                    
                    # Đặt màu dựa trên nội dung thông báo
                    if "đã hết hạn" in message:
                        self.expiry_label.setStyleSheet("color: #FF5722; margin-top: 5px;")  # Màu cam đỏ
                    elif "Hết hạn hôm nay" in message or "Còn 1 ngày" in message:
                        self.expiry_label.setStyleSheet("color: #FFC107; margin-top: 5px;")  # Màu vàng
                    else:
                        self.expiry_label.setStyleSheet("color: #4CAF50; margin-top: 5px;")  # Màu xanh lá
                else:
                    # Nếu không có thông tin hết hạn, chỉ hiển thị HWID
                    self.code_label.setText(self.hwid)
                    self.code_label.setStyleSheet("color: #4CAF50; margin-top: 20px; margin-bottom: 20px;")
                    self.expiry_label.setVisible(False)
                
                # Ẩn nút kích hoạt và sao chép, hiển thị nút đăng nhập
                self.copy_button.setVisible(False)
                self.activate_button.setVisible(False)
                self.login_button.setEnabled(True)
                self.login_button.setText(" ĐĂNG NHẬP")
                
                # Đặt icon cho nút đăng nhập
                try:
                    icon_path = os.path.join(APP_ROOT, "assets", "icons", "fingerprint-alt-svgrepo-com.svg")
                    fingerprint_icon = QIcon(icon_path)
                    if not fingerprint_icon.isNull():
                        self.login_button.setIcon(fingerprint_icon)
                        self.login_button.setIconSize(self.login_button.sizeHint() / 2.5)
                except Exception as e:
                    print(f"Không thể tải icon đăng nhập: {e}")
                
                self.login_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #4CAF50;
                        border: none;
                        border-radius: 25px;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b3d;
                    }
                """)
            else:
                self.is_activated = False
                # Cập nhật giao diện khi thiết bị chưa kích hoạt
                self.instruction_text_label.set_full_text("THIẾT BỊ CHƯA ĐƯỢC KÍCH HOẠT")
                self.instruction_text_label.setStyleSheet("color: #FF5722;")  # Màu cam đỏ
                self.login_button.setEnabled(False)
                self.login_button.setStyleSheet("""
                    QPushButton {
                        color: #AAAAAA;
                        background-color: #383838;
                        border: 2px solid #555555;
                        border-radius: 25px;
                        padding: 10px;
                    }
                    QPushButton:hover {
                        background-color: #383838;
                    }
                """)
        except ImportError:
            # Fallback nếu không import được module
            self.is_activated = False
            print("Không thể import module manage_device")

    def on_login_clicked(self):
        """Xử lý khi nhấn nút đăng nhập"""
        try:
            # Kiểm tra lại xem thiết bị có được kích hoạt không qua máy chủ
            self.check_activation_with_server()
        except Exception as e:
            print(f"Không thể kết nối đến máy chủ kích hoạt: {e}")
            # Nếu không kết nối được máy chủ, kiểm tra cục bộ
            try:
                from manage_device import check_device_in_db
                self.is_activated, _ = check_device_in_db(self.hwid)
            except Exception as e:
                print(f"Lỗi kiểm tra cơ sở dữ liệu cục bộ: {e}")
        
        if not self.is_activated:
            QMessageBox.warning(
                self, 
                "Cảnh báo", 
                "Thiết bị chưa được kích hoạt. Vui lòng kích hoạt trước khi đăng nhập."
            )
            return
        
        # Hiển thị thông báo đăng nhập thành công
        QMessageBox.information(
            self,
            "Thành công",
            "Đăng nhập thành công! Phần mềm sẽ được khởi động."
        )
        
        print("Đăng nhập thành công!")
        # Đánh dấu đã đăng nhập thành công
        self.login_confirmed = True
        
        # Gọi callback để thông báo đăng nhập thành công
        if callable(self.login_confirmed_signal):
            self.login_confirmed_signal()
        
        # Đóng cửa sổ đăng nhập
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())