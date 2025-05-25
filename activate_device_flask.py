import sys
import os
import json
import webbrowser
import threading
import socket
import time
import re
import hashlib
import uuid
from flask import Flask, request, jsonify, render_template_string, redirect, url_for

# Import cơ sở dữ liệu
try:
    from manage_device import Database
except ImportError:
    print("Không thể import module manage_device")
    sys.exit(1)

# Cấu hình
ADMIN_PASSWORD = "vtnvip_admin"  # Mật khẩu admin để kích hoạt thủ công
ALLOWED_ADMINS = ["192.168.43.7", "127.0.0.1"]  # Danh sách IP được phép kích hoạt thủ công

# Lấy địa chỉ IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Xác thực HWID
def validate_hwid(hwid):
    """Kiểm tra xem HWID có hợp lệ không"""
    # HWID phải có đúng 10 ký tự và chỉ chứa chữ và số
    if not re.match(r'^[A-F0-9]{10}$', hwid):
        return False, "Mã máy không hợp lệ. Mã máy phải có 10 ký tự và chỉ bao gồm chữ cái in hoa (A-F) và chữ số (0-9)."
    
    return True, "Mã máy hợp lệ"

# Lấy HWID của máy hiện tại (để kiểm tra)
def get_current_hwid():
    """Lấy Hardware ID duy nhất cho máy tính hiện tại"""
    try:
        # Kết hợp thông tin phần cứng để tạo ID duy nhất
        mac = uuid.getnode()
        computer_name = os.getenv('COMPUTERNAME', '') or os.uname().nodename
        username = os.getlogin()
        
        # Tạo chuỗi từ các thông tin thu thập được
        combined = f"{mac}-{computer_name}-{username}"
        
        # Tạo mã hash từ chuỗi thông tin
        hwid = hashlib.md5(combined.encode()).hexdigest().upper()
        
        # Lấy 10 ký tự đầu tiên của mã hash
        return hwid[:10]
    except:
        # Fallback nếu có lỗi
        return hashlib.md5(str(uuid.getnode()).encode()).hexdigest().upper()[:10]

# Tạo ứng dụng Flask
app = Flask(__name__)

# Template HTML cho trang kích hoạt
ACTIVATION_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kích hoạt key VTN VIP</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: rgba(0, 0, 0, 0.5);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            width: 400px;
            text-align: center;
            padding: 20px;
        }
        .info-icon {
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
        }
        h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 15px;
        }
        p {
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 15px;
            box-sizing: border-box;
            font-size: 14px;
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 10px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
        }
        .activate-btn {
            background-color: #2196F3;
            color: white;
        }
        .cancel-btn {
            background-color: #ff7675;
            color: white;
        }
        .message {
            margin-top: 15px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .admin-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px dashed #ccc;
            display: none;
        }
        .admin-toggle {
            color: #999;
            font-size: 12px;
            text-decoration: underline;
            cursor: pointer;
            margin-top: 20px;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="info-icon">i</div>
        <h1>Kích hoạt key</h1>
        <p>Sao chép mã máy trong tool và dán vào ô dưới</p>
        <input type="text" id="hwid-input" placeholder="Nhập mã máy của bạn" value="{{ hwid }}">
        <div id="message" class="message"></div>
        <div class="button-container">
            <button class="activate-btn" onclick="activateKey()">Kích hoạt</button>
            <button class="cancel-btn" onclick="window.close()">Huỷ</button>
        </div>
        
        <span class="admin-toggle" onclick="toggleAdminSection()">Quản trị viên</span>
        
        <div id="admin-section" class="admin-section">
            <h3>Kích hoạt bởi Quản trị viên</h3>
            <input type="password" id="admin-password" placeholder="Mật khẩu quản trị">
            <input type="text" id="admin-hwid" placeholder="HWID cần kích hoạt" value="{{ hwid }}">
            <button class="activate-btn" onclick="adminActivate()">Kích hoạt thiết bị</button>
        </div>
    </div>
    
    <script>
        function showMessage(text, isSuccess) {
            const messageElement = document.getElementById('message');
            messageElement.textContent = text;
            messageElement.className = isSuccess ? 'message success' : 'message error';
            messageElement.style.display = 'block';
            
            if (isSuccess) {
                // Tự động đóng sau 3 giây nếu thành công
                setTimeout(() => {
                    window.close();
                }, 3000);
            }
        }
        
        function toggleAdminSection() {
            const adminSection = document.getElementById('admin-section');
            if (adminSection.style.display === 'block') {
                adminSection.style.display = 'none';
            } else {
                adminSection.style.display = 'block';
            }
        }
        
        async function activateKey() {
            const hwid = document.getElementById('hwid-input').value.trim();
            
            if (!hwid) {
                showMessage('Vui lòng nhập mã máy', false);
                return;
            }
            
            try {
                const response = await fetch('/activate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ hwid })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, true);
                } else {
                    showMessage(data.message || 'Có lỗi xảy ra khi kích hoạt', false);
                }
            } catch (error) {
                showMessage('Không thể kết nối đến máy chủ kích hoạt', false);
                console.error(error);
            }
        }
        
        async function adminActivate() {
            const password = document.getElementById('admin-password').value.trim();
            const hwid = document.getElementById('admin-hwid').value.trim();
            
            if (!password || !hwid) {
                showMessage('Vui lòng nhập mật khẩu và HWID', false);
                return;
            }
            
            try {
                const response = await fetch('/admin/activate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ password, hwid })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(data.message, true);
                } else {
                    showMessage(data.message || 'Có lỗi xảy ra khi kích hoạt', false);
                }
            } catch (error) {
                showMessage('Không thể kết nối đến máy chủ kích hoạt', false);
                console.error(error);
            }
        }
        
        // Bắt sự kiện Enter trên input
        document.getElementById('hwid-input').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                activateKey();
            }
        });
        
        document.getElementById('admin-password').addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                adminActivate();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Trang chủ - Hiển thị trang kích hoạt"""
    hwid = request.args.get('hwid', '')
    # Kiểm tra HWID từ tham số
    if hwid:
        is_valid, _ = validate_hwid(hwid)
        if not is_valid:
            # Nếu HWID không hợp lệ, xóa nó
            hwid = ''
    
    # Hiển thị HWID hiện tại nếu không có HWID hợp lệ
    if not hwid:
        hwid = get_current_hwid()
    
    return render_template_string(ACTIVATION_HTML, hwid=hwid)

@app.route('/activate', methods=['POST'])
def activate():
    """API kích hoạt thiết bị cho người dùng thông thường"""
    data = request.json
    hwid = data.get('hwid', '')
    
    # Kiểm tra HWID
    if not hwid:
        return jsonify({"success": False, "message": "Mã máy không được để trống"})
    
    # Xác thực định dạng HWID
    is_valid, message = validate_hwid(hwid)
    if not is_valid:
        return jsonify({"success": False, "message": message})
    
    # Kiểm tra xem HWID có phải của máy hiện tại không
    current_hwid = get_current_hwid()
    if hwid != current_hwid:
        return jsonify({
            "success": False, 
            "message": f"Mã máy không khớp với thiết bị hiện tại. Vui lòng sử dụng mã: {current_hwid}"
        })
    
    # Kích hoạt thiết bị trong cơ sở dữ liệu
    return _activate_device(hwid)

@app.route('/admin/activate', methods=['POST'])
def admin_activate():
    """API kích hoạt thiết bị dành cho quản trị viên"""
    data = request.json
    password = data.get('password', '')
    hwid = data.get('hwid', '')
    
    # Kiểm tra mật khẩu
    if password != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Mật khẩu quản trị không chính xác"})
    
    # Kiểm tra IP được phép
    client_ip = request.remote_addr
    if client_ip not in ALLOWED_ADMINS:
        print(f"Phát hiện truy cập quản trị viên từ IP không được phép: {client_ip}")
        return jsonify({"success": False, "message": "Địa chỉ IP không được phép truy cập"})
    
    # Kiểm tra HWID
    if not hwid:
        return jsonify({"success": False, "message": "Mã máy không được để trống"})
    
    # Xác thực định dạng HWID
    is_valid, message = validate_hwid(hwid)
    if not is_valid:
        return jsonify({"success": False, "message": message})
    
    # Kích hoạt thiết bị trong cơ sở dữ liệu
    return _activate_device(hwid)

def _activate_device(hwid):
    """Hàm chung để kích hoạt thiết bị trong cơ sở dữ liệu"""
    # Kiểm tra HWID và kích hoạt trong cơ sở dữ liệu
    db = Database()
    
    try:
        # Kiểm tra xem HWID đã tồn tại chưa
        db.cursor.execute("SELECT status FROM devices WHERE hwid = ?", (hwid,))
        result = db.cursor.fetchone()
        
        response = {}
        
        if result:
            # HWID đã tồn tại, kiểm tra trạng thái
            status = result[0]
            if status == "active":
                response = {"success": True, "message": "Thiết bị đã được kích hoạt trước đó"}
            else:
                # Cập nhật trạng thái thành active
                db.update_device(hwid, status="active")
                response = {"success": True, "message": "Đã kích hoạt lại thiết bị thành công"}
        else:
            # Thêm thiết bị mới
            # Tạo ngày hết hạn (mặc định 1 năm)
            from datetime import datetime, timedelta
            activation_date = datetime.now().strftime("%Y-%m-%d")
            expiry_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
            
            success, message = db.add_device(
                hwid=hwid,
                device_name=f"Device_{hwid[:6]}",
                activation_date=activation_date,
                expiry_date=expiry_date,
                status="active"
            )
            
            if success:
                response = {"success": True, "message": "Kích hoạt thành công"}
            else:
                response = {"success": False, "message": message}
    except Exception as e:
        response = {"success": False, "message": f"Lỗi hệ thống: {str(e)}"}
    finally:
        db.close()
    
    return jsonify(response)

def open_browser(url):
    """Mở trình duyệt sau một khoảng thời gian ngắn"""
    time.sleep(1)  # Đợi 1 giây để chắc chắn máy chủ đã khởi động
    webbrowser.open(url)

def start_server():
    """Khởi động máy chủ Flask"""
    local_ip = get_local_ip()
    port = 8000
    
    print(f"Máy chủ kích hoạt đang chạy tại http://{local_ip}:{port}")
    print(f"HWID của máy hiện tại: {get_current_hwid()}")
    
    # Mở trang web trong trình duyệt
    browser_thread = threading.Thread(target=open_browser, args=(f"http://{local_ip}:{port}",))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Khởi động máy chủ Flask
    app.run(host=local_ip, port=port, debug=False)

@app.route('/list-activated', methods=['GET', 'POST'])
def list_activated():
    """API kiểm tra thiết bị đã kích hoạt"""
    # Xử lý cả GET và POST để linh hoạt hơn
    if request.method == 'POST':
        data = request.json
        hwid = data.get('hwid', '')
    else:
        hwid = request.args.get('hwid', '')
    
    # Kiểm tra HWID
    if not hwid:
        return jsonify({"success": False, "message": "Mã máy không được cung cấp", "activated": False})
    
    # Xác thực định dạng HWID
    is_valid, message = validate_hwid(hwid)
    if not is_valid:
        return jsonify({"success": False, "message": message, "activated": False})
    
    # Kiểm tra trong cơ sở dữ liệu
    db = Database()
    try:
        # Lấy thông tin thiết bị
        db.cursor.execute("""
        SELECT status, expiry_date, device_name, user_name 
        FROM devices 
        WHERE hwid = ?
        """, (hwid,))
        result = db.cursor.fetchone()
        
        if not result:
            return jsonify({
                "success": False, 
                "message": "Thiết bị chưa được kích hoạt", 
                "activated": False
            })
        
        status, expiry_date, device_name, user_name = result
        
        # Kiểm tra trạng thái
        if status != "active":
            return jsonify({
                "success": False, 
                "message": f"Thiết bị đã bị {status}", 
                "activated": False,
                "status": status
            })
        
        # Kiểm tra hạn sử dụng
        is_expired = False
        expiry_message = ""
        from datetime import datetime
        
        if expiry_date:
            try:
                # Chuyển đổi định dạng ngày từ YYYY-MM-DD sang DD/MM/YYYY
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                vn_expiry_date = expiry.strftime("%d/%m/%Y")
                now = datetime.now()
                
                if expiry < now:
                    is_expired = True
                    expiry_message = f"Thiết bị đã hết hạn ngày {vn_expiry_date}"
                else:
                    # Tính số ngày còn lại
                    days_left = (expiry - now).days
                    
                    if days_left <= 0:
                        expiry_message = f"Hết hạn hôm nay ({vn_expiry_date})"
                    elif days_left == 1:
                        expiry_message = f"Còn 1 ngày sử dụng (hết hạn ngày {vn_expiry_date})"
                    else:
                        expiry_message = f"Còn {days_left} ngày sử dụng (hết hạn ngày {vn_expiry_date})"
            except ValueError:
                # Nếu không chuyển đổi được, sử dụng giá trị nguyên bản
                expiry_message = f"Hết hạn ngày {expiry_date}"
        
        if is_expired:
            return jsonify({
                "success": False, 
                "message": expiry_message, 
                "activated": False,
                "status": "expired",
                "expiry_date": expiry_date
            })
        
        # Ghi lại lịch sử đăng nhập
        try:
            client_ip = request.remote_addr
            db.log_activation(hwid, "login", client_ip)
        except:
            pass  # Bỏ qua nếu không ghi được lịch sử
        
        # Trả về thông tin thiết bị đã kích hoạt
        return jsonify({
            "success": True, 
            "message": f"Thiết bị đã được kích hoạt. {expiry_message}", 
            "activated": True,
            "device_info": {
                "hwid": hwid,
                "device_name": device_name or f"Device_{hwid[:6]}",
                "user_name": user_name or "Unknown",
                "status": status,
                "expiry_date": vn_expiry_date if 'vn_expiry_date' in locals() else expiry_date,
                "expiry_message": expiry_message
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Lỗi kiểm tra: {str(e)}", 
            "activated": False,
            "error": str(e)
        })
    finally:
        db.close()

@app.route('/admin/devices', methods=['GET'])
def admin_list_devices():
    """API liệt kê tất cả thiết bị cho quản trị viên"""
    # Kiểm tra mật khẩu admin từ query parameter
    admin_password = request.args.get('password', '')
    if admin_password != ADMIN_PASSWORD:
        return jsonify({"success": False, "message": "Mật khẩu quản trị không chính xác"})
    
    # Kiểm tra IP được phép
    client_ip = request.remote_addr
    if client_ip not in ALLOWED_ADMINS:
        print(f"Phát hiện truy cập quản trị viên từ IP không được phép: {client_ip}")
        return jsonify({"success": False, "message": "Địa chỉ IP không được phép truy cập"})
    
    # Lấy danh sách thiết bị
    db = Database()
    try:
        devices = db.get_all_devices()
        
        device_list = []
        for device in devices:
            device_list.append({
                "id": device[0],
                "hwid": device[1],
                "device_name": device[2] or f"Device_{device[1][:6]}",
                "user_name": device[3] or "Unknown",
                "email": device[4] or "",
                "activation_date": device[5] or "",
                "expiry_date": device[6] or "",
                "status": device[7] or "unknown",
                "notes": device[8] or ""
            })
        
        return jsonify({
            "success": True,
            "message": f"Tìm thấy {len(device_list)} thiết bị",
            "devices": device_list
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Lỗi khi lấy danh sách thiết bị: {str(e)}"
        })
    finally:
        db.close()

if __name__ == "__main__":
    start_server() 