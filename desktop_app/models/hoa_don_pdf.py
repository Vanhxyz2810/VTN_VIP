#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import tất cả các module cần thiết
import os
import datetime
import locale
from num2words import num2words
import random
import hashlib
import urllib.parse
import urllib.request
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, Flowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.graphics.barcode import qr

# Đặt locale cho tiếng Việt
try:
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'vi_VN')
    except:
        pass

# Màu chủ đạo theo logo VTN
VTN_YELLOW = colors.Color(1, 0.7, 0, 1)         # Màu vàng #FFB300
VTN_ORANGE = colors.Color(1, 0.6, 0, 1)         # Màu cam #FF9800
VTN_LIGHT_YELLOW = colors.Color(1, 0.98, 0.9, 1) # Màu vàng nhạt #FFFDE7
VTN_DARK_BG = colors.Color(0.12, 0.12, 0.12, 1) # Màu nền tối #1E1E1E
VTN_TEXT = colors.Color(0.93, 0.93, 0.93, 1)    # Màu chữ sáng #EEEEEE

# Flowable tùy chỉnh cho badge đã thanh toán
class PaidStamp(Flowable):
    """Tạo hình đóng dấu THANH TOÁN"""
    def __init__(self, width=60, height=60):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        
    def draw(self):
        # Lưu trạng thái
        self.canv.saveState()
        
        # Tạo biểu tượng dấu thanh toán
        self.canv.setStrokeColor(colors.green)
        self.canv.setFillColor(colors.Color(0, 0.6, 0, 0.3))  # Màu xanh lá nhạt
        self.canv.setLineWidth(2)
        
        # Vẽ hình tròn
        self.canv.circle(self.width/2, self.height/2, min(self.width, self.height)/2 - 5, stroke=1, fill=1)
        
        # Vẽ dấu tích bên trong
        self.canv.setStrokeColor(colors.white)
        self.canv.setLineWidth(3)
        
        # Tạo dấu tích
        self.canv.line(self.width/2 - 15, self.height/2, self.width/2 - 5, self.height/2 - 10)
        self.canv.line(self.width/2 - 5, self.height/2 - 10, self.width/2 + 15, self.height/2 + 10)
        
        # Phục hồi trạng thái
        self.canv.restoreState()

# Tạo class DocTemplate tùy chỉnh để thêm màu nền và trang trí
class HoaDonPDFTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
        template = PageTemplate('normal', [Frame(
            self.leftMargin, self.bottomMargin, self.width, self.height, id='normal'
        )], onPage=self.add_page_design)
        self.addPageTemplates([template])
    
    def add_page_design(self, canvas, doc):
        width, height = doc.pagesize
        
        # Đặt màu nền tối cho toàn bộ trang
        canvas.saveState()
        canvas.setFillColor(VTN_DARK_BG)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        
        # Tạo viền màu vàng cam ở trên với bo góc
        canvas.setFillColor(VTN_ORANGE)
        # Vẽ hình chữ nhật bo góc bên phải
        radius = 15
        canvas.roundRect(0, height-35, width, 35, radius, fill=1, stroke=0)
        
        # Tạo viền màu vàng ở dưới với bo góc
        canvas.setFillColor(VTN_YELLOW)
        canvas.roundRect(0, 0, width, 12, radius, fill=1, stroke=0)
        
        # Thêm ngày tháng ở góc trên phải
        canvas.setFillColor(colors.white)
        canvas.setFont("Roboto", 9)
        
        # Format ngày tháng
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        canvas.drawRightString(width-25, height-22, f"Ngày: {today}")
        
        # Thêm watermark mờ
        canvas.saveState()
        canvas.setFont("Roboto-Bold", 50)
        canvas.setFillColor(VTN_LIGHT_YELLOW)
        canvas.setFillAlpha(0.03)  # Làm mờ hơn
        
        # Tạo watermark hình thức phức tạp hơn
        for i in range(5):
            x_pos = random.randint(50, int(width)-50)
            y_pos = random.randint(50, int(height)-50)
            rotation = random.randint(0, 359)
            
            canvas.saveState()
            canvas.translate(x_pos, y_pos)
            canvas.rotate(rotation)
            canvas.drawCentredString(0, 0, "VTN VIP")
            canvas.restoreState()
        
        canvas.restoreState()
        
        # Thêm footer hiện đại
        canvas.saveState()
        canvas.setFillColor(colors.Color(0.15, 0.15, 0.15, 1))
        canvas.roundRect(width/2 - 220, 15, 440, 25, 10, fill=1, stroke=0)
        
        canvas.setFont("Roboto", 8)
        canvas.setFillColor(colors.white)
        canvas.drawCentredString(width/2, 27, "Cảm ơn quý khách đã sử dụng dịch vụ | Hotline: 19009000")
        
        canvas.restoreState()



# Thay đổi hàm tạo QR để sử dụng VietQR
def create_viet_qr(ma_hoa_don, amount):
    """Tạo mã QR sử dụng VietQR API"""
    try:
        # Định dạng thông tin thanh toán
        addInfo = f"Thanh toan hoa don {ma_hoa_don}"
        accountName = "Cong Ty Dien Luc VTN VIP"
        
        # URL encode các tham số
        encoded_info = urllib.parse.quote(addInfo)
        encoded_name = urllib.parse.quote(accountName)
        
        # Tạo URL đến VietQR API
        url = f"https://img.vietqr.io/image/mbbank-9728102006-compact2.jpg?amount={int(amount)}&addInfo={encoded_info}&accountName={encoded_name}"
        
        # Tải hình ảnh từ URL
        img_data = urllib.request.urlopen(url).read()
        img_file = BytesIO(img_data)
        
        # Trả về đối tượng Image của ReportLab
        return Image(img_file, width=150, height=150)
    except Exception as e:
        print(f"Lỗi khi tạo mã QR VietQR: {e}")
        # Sử dụng QR thông thường nếu có lỗi xảy ra


class HoaDonPDF:
    def __init__(self):
        # Đăng ký font Roboto hỗ trợ tiếng Việt
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Tìm font Roboto trong các vị trí có thể
        font_paths = [
            # Tìm trong thư mục font
            os.path.join(base_dir, 'font', 'Roboto-Regular.ttf'),
            os.path.join(base_dir, 'font', 'static', 'Roboto-Regular.ttf'),
            os.path.join(base_dir, 'desktop_app', 'font', 'Roboto-Regular.ttf'),
            os.path.join(base_dir, 'desktop_app', 'font', 'static', 'Roboto-Regular.ttf'),
            # Tìm trong thư mục assets
            os.path.join(base_dir, 'assets', 'fonts', 'Roboto-Regular.ttf'),
            os.path.join(base_dir, 'desktop_app', 'assets', 'fonts', 'Roboto-Regular.ttf'),
        ]
        
        font_regular_path = None
        for path in font_paths:
            if os.path.exists(path):
                font_regular_path = path
                break
                
        if not font_regular_path:
            print("Không tìm thấy font Roboto Regular")
            return
            
        # Tìm font Roboto Bold
        bold_font_paths = [
            # Thay Regular bằng Bold trong đường dẫn đã tìm được
            path.replace('Regular', 'Bold') for path in font_paths
        ]
        
        font_bold_path = None
        for path in bold_font_paths:
            if os.path.exists(path):
                font_bold_path = path
                break
                
        if not font_bold_path:
            print("Không tìm thấy font Roboto Bold, sử dụng Regular")
            font_bold_path = font_regular_path
        
        # Đăng ký các font
        try:
            pdfmetrics.registerFont(TTFont('Roboto', font_regular_path))
            pdfmetrics.registerFont(TTFont('Roboto-Bold', font_bold_path))
        except Exception as e:
            print(f"Lỗi khi đăng ký font: {e}")
        
        # Tạo style cho các phần văn bản - màu sáng trên nền tối
        self.styles = getSampleStyleSheet()
        
        # Style cho tiêu đề chính - màu trắng
        self.title_style = ParagraphStyle(
            name='Title_Style',
            fontName='Roboto-Bold',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=VTN_ORANGE
        )
        
        # Style cho subtitle
        self.subtitle_style = ParagraphStyle(
            name='Subtitle_Style',
            fontName='Roboto',
            fontSize=10,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.white
        )
        
        # Style cho heading chính
        self.heading_style = ParagraphStyle(
            name='Heading_Style',
            fontName='Roboto-Bold',
            fontSize=12,
            leading=16,
            textColor=VTN_YELLOW,
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Style cho company text
        self.company_style = ParagraphStyle(
            name='Company_Style',
            fontName='Roboto-Bold',
            fontSize=11,
            leading=16,
            textColor=VTN_ORANGE
        )
        
        # Style cho tiêu đề thông tin khách hàng 
        self.customer_label_style = ParagraphStyle(
            name='Customer_Label_Style',
            fontName='Roboto-Bold',
            fontSize=10,
            leading=14,
            textColor=colors.white
        )
        
        # Style cho giá trị thông tin
        self.value_style = ParagraphStyle(
            name='Value_Style',
            fontName='Roboto',
            fontSize=10,
            leading=14,
            textColor=colors.white
        )
        
        # Style cho tổng tiền
        self.summary_style = ParagraphStyle(
            name='Summary_Style',
            fontName='Roboto-Bold',
            fontSize=14,
            leading=16,
            alignment=TA_RIGHT,
            textColor=VTN_ORANGE
        )
        
        # Style cho thông tin hóa đơn
        self.invoice_info_style = ParagraphStyle(
            name='Invoice_Info',
            fontName='Roboto',
            fontSize=9,
            leading=12,
            textColor=colors.white
        )
        
        # Style cho mã hóa đơn
        self.invoice_code_style = ParagraphStyle(
            name='Invoice_Code',
            fontName='Roboto-Bold',
            fontSize=12,
            leading=14,
            textColor=VTN_YELLOW
        )
    
    def doc_so_thanh_chu(self, number):
        """Chuyển đổi số thành chữ tiếng Việt"""
        if number is None:
            return "Không đồng"
            
        try:
            # Phương pháp 1: Sử dụng num2words
            text = num2words(int(number), lang='vi')
            text = text.replace(',', '').replace('-', ' ').title()
            return f"{text} Đồng"
        except Exception as e:
            print(f"Lỗi khi chuyển đổi số thành chữ: {e}")
            # Phương pháp 2: Đơn giản hóa
            try:
                number = int(number)
                thousands = number // 1000
                remainder = number % 1000
                
                if remainder == 0:
                    return f"{thousands} Nghìn Đồng"
                else:
                    return f"{thousands} Nghìn {remainder} Đồng"
            except:
                return "Không đồng"
                
    def tao_hoa_don(self, hoa_don, khach_hang, bang_gia, output_dir="exports"):
        """Tạo file PDF hóa đơn điện - phiên bản chuyên nghiệp"""
        # Kiểm tra dữ liệu đầu vào
        if hoa_don is None or khach_hang is None or bang_gia is None:
            print("Dữ liệu đầu vào không hợp lệ")
            return None
            
        # Đảm bảo các thuộc tính của hóa đơn không bị None
        ma_hoa_don = getattr(hoa_don, 'ma_hoa_don', 'N/A')
        thang = getattr(hoa_don, 'thang', 'N/A')
        nam = getattr(hoa_don, 'nam', 'N/A')
        da_thanh_toan = getattr(hoa_don, 'da_thanh_toan', False)
        chi_so_dau = getattr(hoa_don, 'chi_so_dau', 0)
        chi_so_cuoi = getattr(hoa_don, 'chi_so_cuoi', 0)
        
        # Tính lượng tiêu thụ
        tieu_thu = getattr(hoa_don, 'tieu_thu', None)
        if tieu_thu is None:
            tieu_thu = chi_so_cuoi - chi_so_dau
        
        # Đảm bảo thư mục lưu tồn tại
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir_full = os.path.join(base_dir, output_dir)
        
        try:
            os.makedirs(output_dir_full, exist_ok=True)
        except Exception as e:
            print(f"Lỗi khi tạo thư mục xuất PDF: {e}")
            # Fallback: sử dụng thư mục hiện tại
            output_dir_full = os.path.dirname(os.path.abspath(__file__))
        
        # Tạo tên file với đường dẫn đầy đủ
        file_name = os.path.join(output_dir_full, f"hoa_don_{ma_hoa_don}.pdf")
        
        print(f"Đang tạo file PDF tại: {file_name}")
        
        # Khởi tạo các biến và tài liệu PDF
        elements = []
        doc = HoaDonPDFTemplate(file_name, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=45, bottomMargin=40)
        
        # Tìm đường dẫn logo
        logo_path = None
        logo_paths = [
            os.path.join(base_dir, 'imgs', 'vtn_vip.png'),
            os.path.join(base_dir, 'imgs', '@vtn_vip.png'),
            os.path.join(base_dir, 'desktop_app', 'imgs', 'vtn_vip.png'),
            os.path.join(base_dir, 'desktop_app', 'assets', 'images', 'vtn_vip.png'),
            os.path.join(base_dir, 'desktop_app', 'assets', 'vtn_vip.png'),
            os.path.join(base_dir, 'assets', 'imgs', 'vtn_vip.png'),
            os.path.join(base_dir, 'assets', 'images', 'vtn_vip.png')
        ]
        
        for path in logo_paths:
            if os.path.exists(path):
                logo_path = path
                break
        
        # Khởi tạo thông tin cho mã QR
        qr_data = (f"HD:{ma_hoa_don}|KH:{khach_hang.ma_khach_hang}|"
                  f"Tháng:{thang}/{nam}|"
                  f"Tiêu thụ:{tieu_thu}kWh|"
                  f"Thanh toán:{da_thanh_toan}")
        
        # ===== HEADER & LOGO =====
        # Tạo bảng header với logo và thông tin công ty
        if logo_path and os.path.exists(logo_path):
            logo = Image(logo_path, width=100, height=35)
            
            company_info = [
                Paragraph("CÔNG TY ĐIỆN LỰC VTN VIP", self.company_style),
                Paragraph("MST: 0100100079", self.invoice_info_style),
                Paragraph("Hotline: 19009000", self.invoice_info_style)
            ]
            
            # Thay đổi cách hiển thị header không có thanh ngang
            company_table = Table([
                [logo, 
                 Table([
                     [Paragraph("HÓA ĐƠN TIỀN ĐIỆN", self.title_style)],
                     [Paragraph(f"Kỳ thanh toán: Tháng {thang}/{nam}", self.subtitle_style)]
                 ], colWidths=[380])
                ],
                [Paragraph(f"Mã hóa đơn: {ma_hoa_don}", self.invoice_code_style),
                 Table([company_info], colWidths=[380])
                ]
            ], colWidths=[120, 380])
            
            company_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (0, -1), 0),
                ('RIGHTPADDING', (0, 0), (0, -1), 10),
            ]))
            
            elements.append(company_table)
        else:
            # Nếu không có logo, hiển thị tiêu đề đơn giản
            elements.append(Paragraph("HÓA ĐƠN TIỀN ĐIỆN", self.title_style))
            elements.append(Paragraph(f"Mã hóa đơn: {ma_hoa_don} | Tháng {thang}/{nam}", self.subtitle_style))
            
        elements.append(Spacer(1, 20))
        
        # ===== THÔNG TIN KHÁCH HÀNG VÀ MÃ QR =====
        # Lấy thông tin khách hàng
        ho_ten = getattr(khach_hang, 'ho_ten', 'N/A')
        dia_chi = getattr(khach_hang, 'dia_chi', 'N/A')
        ma_khach_hang = getattr(khach_hang, 'ma_khach_hang', 'N/A')
        so_dien_thoai = getattr(khach_hang, 'so_dien_thoai', 'N/A')
        ma_cong_to = getattr(khach_hang, 'ma_cong_to', 'N/A')
        
        # === Thiết kế riêng phần khách hàng và QR code ===
        # Thông tin khách hàng - thiết kế đẹp mắt hơn
        # Tạo style riêng cho nhãn và giá trị
        label_style = ParagraphStyle(
            name='Label_Style',
            fontName='Roboto-Bold',
            fontSize=9,
            leading=12,
            textColor=VTN_YELLOW
        )

        value_style = ParagraphStyle(
            name='Value_Style',
            fontName='Roboto',
            fontSize=10,
            leading=12,
            textColor=colors.white
        )

        # Tạo bảng thông tin khách hàng với thiết kế mới đẹp mắt hơn
        customer_header = Table([[Paragraph("THÔNG TIN KHÁCH HÀNG", self.heading_style)]], 
                              colWidths=[480])
        customer_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.15, 0.15, 0.15, 1)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))

        # Tạo bảng chứa nội dung thông tin khách hàng
        customer_content = [
            # Dòng 1: Tên khách hàng (trên toàn bộ chiều rộng)
            [Paragraph("<b>Tên khách hàng:</b>", label_style), 
             Paragraph(ho_ten, value_style), '', ''],
            
            # Dòng 2: Mã khách hàng | Số điện thoại
            [Paragraph("<b>Mã khách hàng:</b>", label_style), 
             Paragraph(ma_khach_hang, value_style),
             Paragraph("<b>Số điện thoại:</b>", label_style), 
             Paragraph(so_dien_thoai, value_style)],
             
            # Dòng 3: Địa chỉ (trên toàn bộ chiều rộng)
            [Paragraph("<b>Địa chỉ:</b>", label_style), 
             Paragraph(dia_chi, value_style), '', ''],
             
            # Dòng 4: Mã công tơ | Ngày xuất
            [Paragraph("<b>Mã công tơ:</b>", label_style), 
             Paragraph(ma_cong_to, value_style),
             Paragraph("<b>Ngày xuất:</b>", label_style), 
             Paragraph(datetime.datetime.now().strftime('%d/%m/%Y'), value_style)]
        ]

        customer_info = Table(customer_content, colWidths=[100, 140, 100, 140])
        customer_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.18, 0.18, 0.18, 1)),
            ('SPAN', (1, 0), (3, 0)),  # Gộp 3 ô cho tên khách hàng
            ('SPAN', (1, 2), (3, 2)),  # Gộp 3 ô cho địa chỉ
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # Căn phải tất cả các nhãn
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),  # Căn phải tất cả các nhãn ở cột 3
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.Color(0.22, 0.22, 0.22, 1)),  # Thêm đường kẻ mờ giữa các ô
        ]))

        # Kết hợp header và nội dung vào một bảng chính
        customer_table = Table([
            [customer_header],
            [customer_info]
        ], colWidths=[480])
        customer_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
            ('LINEBELOW', (0, 0), (0, 0), 1, VTN_YELLOW),  # Đường kẻ dưới header
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))

        elements.append(customer_table)
        elements.append(Spacer(1, 15))
        
        # Tạo QR code riêng với nền trắng sử dụng VietQR
        # Tạo QR code từ VietQR
        tong_tien = getattr(hoa_don, 'so_tien', 0)
        if tong_tien is None:
            tong_tien = 0
        viet_qr = create_viet_qr(ma_hoa_don, tong_tien)
        qr_table = Table([
            [Paragraph("QUÉT MÃ THANH TOÁN", self.heading_style)],
            [viet_qr]
        ], colWidths=[160])

        qr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.Color(0.15, 0.15, 0.15, 1)),
            ('BACKGROUND', (0, 1), (0, 1), colors.white),  # Nền trắng cho QR
            ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (0, -1), 10),
            ('RIGHTPADDING', (0, 0), (0, -1), 10),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8),
            ('TOPPADDING', (0, 1), (0, 1), 10),
            ('BOTTOMPADDING', (0, 1), (0, 1), 10),
            ('BOX', (0, 0), (0, -1), 1, VTN_YELLOW),
            ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ]))

        # Thêm QR code riêng biệt sau phần thông tin chi tiết
        elements.append(Spacer(1, 5))
        elements.append(qr_table)
        
        # ===== THÔNG TIN CHỈ SỐ =====
        elements.append(Paragraph("CHỈ SỐ CÔNG TƠ VÀ TIÊU THỤ", self.heading_style))
        
        # Bảng chỉ số
        chi_so_data = [
            ['CHỈ SỐ ĐẦU KỲ', 'CHỈ SỐ CUỐI KỲ', 'SẢN LƯỢNG (kWh)'],
            [str(chi_so_dau), str(chi_so_cuoi), str(tieu_thu)]
        ]
        
        chi_so_table = Table(chi_so_data, colWidths=[160, 160, 160])
        chi_so_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), VTN_ORANGE),
            ('BACKGROUND', (0, 1), (-1, 1), colors.Color(0.18, 0.18, 0.18, 1)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        
        elements.append(chi_so_table)
        elements.append(Spacer(1, 15))
        
        # ===== TỔNG TIỀN =====
        try:
            # Tổng tiền (đã bao gồm VAT)
            tong_tien = getattr(hoa_don, 'so_tien', 0)
            if tong_tien is None:
                tong_tien = 0
        except Exception as e:
            print(f"Lỗi khi lấy số tiền: {e}")
            tong_tien = 0
        
        # Hiển thị số tiền bằng chữ
        try:
            so_tien_bang_chu = self.doc_so_thanh_chu(int(tong_tien))
        except:
            so_tien_bang_chu = "Không đồng"
            
        # Bảng tổng cộng - thiết kế hiện đại
        tong_cong_data = [
            ['KHOẢN MỤC', 'THÀNH TIỀN (đ)'],
            ['TỔNG CỘNG (đã bao gồm VAT)', f"{int(tong_tien):,}".replace(',', '.')]
        ]
        
        tong_cong_table = Table(tong_cong_data, colWidths=[240, 240])
        tong_cong_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), VTN_ORANGE),
            ('BACKGROUND', (0, 1), (-1, 1), VTN_DARK_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Roboto-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        
        elements.append(tong_cong_table)
        elements.append(Spacer(1, 10))
        
        # Hiển thị số tiền bằng chữ
        elements.append(Paragraph(f"<i>Bằng chữ: <b>{so_tien_bang_chu}</b></i>", self.value_style))
        
        # Thêm dấu đã thanh toán nếu đã thanh toán
        if da_thanh_toan:
            elements.append(Spacer(1, 10))
            
            # Tạo bảng chứa thông tin thanh toán và dấu đã thanh toán
            payment_info = [
                [Paragraph(f"<font color='green'>ĐÃ THANH TOÁN</font>", 
                        ParagraphStyle('PaymentStyle', parent=self.value_style, 
                                      fontSize=14, alignment=TA_CENTER, fontName='Roboto-Bold')),
                PaidStamp()]
            ]
            
            payment_table = Table(payment_info, colWidths=[400, 80])
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
            ]))
            
            elements.append(payment_table)
        else:
            # Hiển thị trạng thái chưa thanh toán
            trang_thai_style = ParagraphStyle(
                name='TrangThai_Style',
                fontName='Roboto-Bold',
                fontSize=14,
                leading=16,
                textColor='red',
                alignment=TA_CENTER,
                spaceBefore=15
            )
            
            elements.append(Paragraph("CHƯA THANH TOÁN", trang_thai_style))
        
        # Thêm thông tin bổ sung và lưu ý
        elements.append(Spacer(1, 20))
        
        note_style = ParagraphStyle(
            name='Note_Style',
            fontName='Roboto',
            fontSize=9,
            textColor=colors.lightgrey,
            alignment=TA_LEFT
        )
        
        elements.append(Paragraph(
            "<i>Lưu ý: Hóa đơn này đã được số hóa và có giá trị pháp lý tương đương với hóa đơn giấy. "
            "Quý khách có thể thanh toán qua các kênh ngân hàng, ví điện tử hoặc tại các điểm thu hộ được ủy quyền.</i>", 
            note_style
        ))
        
        # Build the PDF
        try:
            doc.build(elements)
            return file_name
        except Exception as e:
            print(f"Lỗi khi tạo file PDF: {e}")
            return None

# Hàm tiện ích để tạo hóa đơn trực tiếp từ mã hóa đơn
def tao_hoa_don_pdf(hoa_don, khach_hang, bang_gia, output_dir="exports"):
    """Hàm tiện ích để tạo hóa đơn PDF"""
    # Tạo một instance mới để tránh lỗi reference
    try:
        # Tạo PDF generator và tạo hóa đơn
        generator = HoaDonPDF()
        return generator.tao_hoa_don(hoa_don, khach_hang, bang_gia, output_dir)
    except Exception as e:
        print(f"Lỗi khi tạo hóa đơn PDF: {e}")
        return None 