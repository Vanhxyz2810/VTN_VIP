# Mẫu Code Từ Các File Lớn

## 1. Lấy HWID từ file login_form.py

```python
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
        
        return hwid
    except Exception as e:
        print(f"Lỗi khi lấy HWID: {e}")
        return "UNKNOWN-HWID"
```

## 2. Tạo HTML Kích hoạt từ file login_form.py

```python
def create_activation_html(hwid, output_path="activation.html"):
    """Tạo trang HTML để người dùng gửi thông tin kích hoạt"""
    html_content = f"""<!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Kích hoạt VTN VIP</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                color: #333;
            }}
            .container {{
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                width: 90%;
                max-width: 600px;
                padding: 2rem;
                text-align: center;
            }}
            h1 {{
                color: #2c3e50;
                margin-bottom: 1.5rem;
            }}
            .hwid-box {{
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 1rem;
                margin: 1.5rem 0;
                font-family: 'Courier New', Courier, monospace;
                font-size: 1.2rem;
                word-break: break-all;
                position: relative;
            }}
            .copy-btn {{
                position: absolute;
                top: 0.5rem;
                right: 0.5rem;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 0.3rem 0.6rem;
                cursor: pointer;
                font-size: 0.8rem;
                transition: background-color 0.2s;
            }}
            .copy-btn:hover {{
                background-color: #0069d9;
            }}
            .instructions {{
                text-align: left;
                margin: 1.5rem 0;
                line-height: 1.6;
            }}
            .btn {{
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 0.8rem 2rem;
                font-size: 1rem;
                cursor: pointer;
                transition: background-color 0.2s;
                margin-top: 1rem;
                text-decoration: none;
                display: inline-block;
            }}
            .btn:hover {{
                background-color: #218838;
            }}
            .footer {{
                margin-top: 2rem;
                font-size: 0.9rem;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Kích hoạt Phần Mềm VTN VIP</h1>
            <p>Vui lòng sao chép mã HWID bên dưới và gửi cho quản trị viên để được kích hoạt phần mềm:</p>
            
            <div class="hwid-box">
                <span id="hwid">{hwid}</span>
                <button class="copy-btn" onclick="copyHWID()">Sao chép</button>
            </div>
            
            <div class="instructions">
                <h3>Hướng dẫn:</h3>
                <ol>
                    <li>Sao chép mã HWID ở trên bằng cách nhấn vào nút "Sao chép"</li>
                    <li>Gửi mã HWID cho quản trị viên qua email hoặc tin nhắn</li>
                    <li>Chờ xác nhận kích hoạt từ quản trị viên</li>
                    <li>Sau khi được kích hoạt, khởi động lại phần mềm VTN VIP</li>
                </ol>
            </div>
            
            <a href="mailto:admin@vtn-vip.com?subject=Yêu%20cầu%20kích%20hoạt%20VTN%20VIP&body=Xin%20chào%20quản%20trị%20viên,%0A%0ATôi%20muốn%20yêu%20cầu%20kích%20hoạt%20phần%20mềm%20VTN%20VIP.%0AMã%20HWID%20của%20tôi%20là:%20{hwid}%0A%0AXin%20cảm%20ơn!" class="btn">Gửi Email Yêu Cầu</a>
            
            <div class="footer">
                <p>© 2024 VTN VIP - Hệ thống quản lý điện</p>
            </div>
        </div>
        
        <script>
            function copyHWID() {{
                const hwid = document.getElementById('hwid');
                const textArea = document.createElement('textarea');
                textArea.value = hwid.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                const copyBtn = document.querySelector('.copy-btn');
                copyBtn.textContent = 'Đã sao chép!';
                setTimeout(() => {{
                    copyBtn.textContent = 'Sao chép';
                }}, 2000);
            }}
        </script>
    </body>
    </html>
    """
    
    # Lưu nội dung HTML vào file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return True
    except Exception as e:
        print(f"Lỗi khi tạo file HTML: {e}")
        return False
```

## 3. Xác thực thiết bị từ file manage_device.py

```python
def check_device_in_db(hwid):
    """
    Kiểm tra xem thiết bị có trong cơ sở dữ liệu không
    
    Args:
        hwid (str): Hardware ID của thiết bị cần kiểm tra
        
    Returns:
        tuple: (is_valid, message) - is_valid là True nếu thiết bị hợp lệ,
                                    message là thông báo chi tiết
    """
    try:
        # Kết nối đến cơ sở dữ liệu
        conn = sqlite3.connect('devices.db')
        cursor = conn.cursor()
        
        # Kiểm tra xem bảng devices đã tồn tại chưa
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='devices'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Tạo bảng nếu chưa tồn tại
            cursor.execute('''
                CREATE TABLE devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hwid TEXT UNIQUE NOT NULL,
                    device_name TEXT,
                    owner_name TEXT,
                    activation_date TEXT,
                    expiration_date TEXT,
                    status TEXT DEFAULT 'active',
                    notes TEXT
                )
            ''')
            conn.commit()
            conn.close()
            return False, "Thiết bị chưa được kích hoạt"
        
        # Kiểm tra thiết bị trong cơ sở dữ liệu
        cursor.execute("SELECT * FROM devices WHERE hwid=? AND status='active'", (hwid,))
        device = cursor.fetchone()
        
        if device:
            # Nếu tìm thấy thiết bị và đang hoạt động
            conn.close()
            return True, "Thiết bị hợp lệ"
        else:
            # Kiểm tra xem thiết bị có tồn tại nhưng bị vô hiệu hóa không
            cursor.execute("SELECT status FROM devices WHERE hwid=?", (hwid,))
            inactive_device = cursor.fetchone()
            
            if inactive_device:
                conn.close()
                return False, f"Thiết bị đã bị vô hiệu hóa: {inactive_device[0]}"
            else:
                conn.close()
                return False, "Thiết bị chưa được kích hoạt"
    
    except Exception as e:
        # Xử lý ngoại lệ
        print(f"Lỗi khi kiểm tra thiết bị: {e}")
        return True, "Lỗi khi kiểm tra thiết bị, cho phép sử dụng tạm thời"
```

## 4. Khởi động ứng dụng từ file desktop_app/main.py

```python
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
    
    # Khởi tạo handler xử lý đăng nhập
    login_handler = LoginHandler()
    
    # Khởi tạo cửa sổ đăng nhập
    login_window = LoginWindow()
    
    # Kết nối tín hiệu đăng nhập thành công
    login_window.login_confirmed_signal = login_handler.on_login_success
    
    # Hiển thị cửa sổ đăng nhập
    login_window.show()
    app.exec()
    
    # Kiểm tra trạng thái đăng nhập
    if login_handler.login_successful:
        print("Đăng nhập thành công, mở ứng dụng chính...")
        # Khởi tạo DatabaseHandler
        db = DatabaseHandler()
        
        # Làm tròn số tiền trong hóa đơn (loại bỏ số thập phân thừa)
        db.lam_tron_so_tien_hoa_don()
        
        # Khởi tạo cửa sổ chính
        window = MainWindow(db)
        window.show()
        
        # Chạy vòng lặp sự kiện cho cửa sổ chính
        return_code = app.exec()
        sys.exit(return_code)
    else:
        print("Đăng nhập thất bại hoặc người dùng đã hủy.")
        sys.exit(0)
```