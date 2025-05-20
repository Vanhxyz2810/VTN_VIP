#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame
import os
import datetime
from num2words import num2words
import locale

# Đặt locale cho tiếng Việt
try:
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'vi_VN')
    except:
        pass

# Màu chủ đạo
VTN_YELLOW = colors.Color(1, 0.7, 0, 1)  # Màu vàng đậm
VTN_GRAY = colors.Color(0.9, 0.9, 0.9, 1)  # Màu xám đậm hơn

# Tạo class DocTemplate tùy chỉnh để thêm màu nền
class HoaDonPDFTemplate(BaseDocTemplate):
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

class HoaDonPDF:
    def __init__(self):
        # Đăng ký font Roboto hỗ trợ tiếng Việt
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Đăng ký font Regular
        font_regular_path = os.path.join(base_dir, 'font', 'Roboto-Regular.ttf')
        if not os.path.exists(font_regular_path):
            font_regular_path = os.path.join(base_dir, 'font', 'static', 'Roboto-Regular.ttf')
            if not os.path.exists(font_regular_path):
                print(f"Không tìm thấy font Roboto-Regular.ttf")
                return
        
        # Đăng ký font Bold
        font_bold_path = os.path.join(base_dir, 'font', 'static', 'Roboto-Bold.ttf')
        if not os.path.exists(font_bold_path):
            print(f"Không tìm thấy font Roboto-Bold.ttf")
            font_bold_path = font_regular_path
        
        # Đăng ký các font
        pdfmetrics.registerFont(TTFont('Roboto', font_regular_path))
        pdfmetrics.registerFont(TTFont('Roboto-Bold', font_bold_path))
        
        # Tạo style cho các phần văn bản
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Normal_VN', fontName='Roboto', fontSize=10, leading=14))
        self.styles.add(ParagraphStyle(name='Title_VN', fontName='Roboto-Bold', fontSize=14, alignment=1, spaceAfter=10))
        self.styles.add(ParagraphStyle(name='Bold_VN', fontName='Roboto-Bold', fontSize=10, leading=14, spaceAfter=6))
        self.styles.add(ParagraphStyle(name='Footer_VN', fontName='Roboto', fontSize=8, leading=10, alignment=1))
        
        # Style cho tiêu đề - màu vàng VTN
        self.title_style = ParagraphStyle(
            name='Title_Style',
            fontName='Roboto-Bold',
            fontSize=14,
            alignment=1,
            spaceAfter=10,
            textColor=VTN_YELLOW
        )
        
        # Style cho subtitle - màu vàng VTN và căn giữa
        self.subtitle_style = ParagraphStyle(
            name='Subtitle_Style',
            fontName='Roboto',
            fontSize=10,
            alignment=1,
            spaceAfter=10,
            textColor=VTN_YELLOW
        )
        
        # Style cho heading
        self.heading_style = ParagraphStyle(
            name='Heading_Style',
            fontName='Roboto-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.black
        )
        
        # Style cho company text đậm - màu vàng VTN
        self.company_style = ParagraphStyle(
            name='Company_Style',
            fontName='Roboto-Bold',
            fontSize=10,
            leading=14,
            textColor=VTN_YELLOW
        )
        
        # Style cho thông tin khách hàng - màu vàng
        self.customer_style = ParagraphStyle(
            name='Customer_Style',
            fontName='Roboto-Bold',
            fontSize=10,
            leading=14,
            textColor=VTN_YELLOW
        )
        
        # Style cho giá trị thông tin - màu đen
        self.value_style = ParagraphStyle(
            name='Value_Style',
            fontName='Roboto',
            fontSize=10,
            leading=14,
            textColor=colors.black
        )
        
        # Style cho footer
        self.footer_style = ParagraphStyle(
            name='Footer_Style',
            fontName='Roboto',
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=colors.black
        )
    
    def doc_so_thanh_chu(self, number):
        """Chuyển đổi số thành chữ tiếng Việt"""
        try:
            # Sử dụng num2words để chuyển đổi số thành chữ
            text = num2words(number, lang='vi')
            
            # Chuẩn hóa chuỗi
            text = text.replace(',', '').replace('-', ' ')
            
            # Chuyển đổi chuỗi thành dạng viết hoa chữ cái đầu từng từ
            words = text.split()
            capitalized_words = [word.capitalize() for word in words]
            text = ' '.join(capitalized_words)
            
            return f"{text} Đồng"
        except Exception:
            # Xử lý fallback nếu num2words không hoạt động
            if number >= 1000000000:  # Tỷ
                ty = number // 1000000000
                remainder = number % 1000000000
                if remainder == 0:
                    return f"{ty} Tỷ Đồng"
                else:
                    trieu = remainder // 1000000
                    remainder = remainder % 1000000
                    if trieu > 0:
                        if remainder == 0:
                            return f"{ty} Tỷ {trieu} Triệu Đồng"
                        else:
                            return f"{ty} Tỷ {trieu} Triệu {remainder} Đồng"
                    else:
                        return f"{ty} Tỷ {remainder} Đồng"
            elif number >= 1000000:  # Triệu
                trieu = number // 1000000
                remainder = number % 1000000
                if remainder == 0:
                    return f"{trieu} Triệu Đồng"
                else:
                    return f"{trieu} Triệu {remainder} Đồng"
            elif number >= 1000:  # Nghìn
                nghin = number // 1000
                remainder = number % 1000
                if remainder == 0:
                    return f"{nghin} Nghìn Đồng"
                else:
                    return f"{nghin} Nghìn {remainder} Đồng"
            else:
                return f"{number} Đồng"

    def tao_hoa_don(self, hoa_don, khach_hang, bang_gia, output_dir="exports"):
        """Tạo file PDF hóa đơn điện"""
        # Đảm bảo thư mục lưu tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Kiểm tra và tính lại tieu_thu nếu cần
        if not hasattr(hoa_don, 'tieu_thu') or hoa_don.tieu_thu is None:
            if hasattr(hoa_don, 'chi_so_cuoi') and hasattr(hoa_don, 'chi_so_dau') and hoa_don.chi_so_cuoi is not None and hoa_don.chi_so_dau is not None:
                hoa_don.tieu_thu = max(0, hoa_don.chi_so_cuoi - hoa_don.chi_so_dau)
            else:
                # Nếu không thể tính được tiêu thụ, gán giá trị mặc định
                hoa_don.tieu_thu = 0
                
        # Tạo tên file
        file_name = f"{output_dir}/hoa_don_{hoa_don.ma_hoa_don}.pdf"
        
        # Tạo tài liệu PDF với nền màu xám
        doc = HoaDonPDFTemplate(file_name, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        
        # Tìm đường dẫn logo
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, 'imgs', 'vtn_vip.png')
        
        # ===== HEADER: LOGO VÀ TIÊU ĐỀ =====
        if os.path.exists(logo_path):
            # Chuẩn bị logo
            logo = Image(logo_path, width=60, height=30, hAlign='LEFT')
            
            # Chuẩn bị tiêu đề
            title = Paragraph("HÓA ĐƠN GTGT (TIỀN ĐIỆN)", self.title_style)
            subtitle = Paragraph("(Bản thể hiện của hóa đơn điện tử)", self.subtitle_style)
            
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
            elements.append(Paragraph("HÓA ĐƠN GTGT (TIỀN ĐIỆN)", self.title_style))
            elements.append(Paragraph("(Bản thể hiện của hóa đơn điện tử)", self.subtitle_style))
        
        elements.append(Spacer(1, 5))
        
        # ===== THÔNG TIN CÔNG TY =====
        elements.append(Paragraph("CÔNG TY ĐIỆN LỰC VTN VIP", self.company_style))
        elements.append(Paragraph("Địa chỉ: <font color='black'>Hà Nội</font>", self.customer_style))
        elements.append(Paragraph("Điện thoại: <font color='black'>19009000</font> - MST: <font color='black'>0100100079</font>", self.customer_style))
        elements.append(Spacer(1, 5))
        
        # ===== THÔNG TIN HÓA ĐƠN =====
        elements.append(Paragraph(f"Mã hóa đơn: <font color='black'>{hoa_don.ma_hoa_don}</font>", self.company_style))
        elements.append(Paragraph(f"Kỳ hóa đơn: Tháng <font color='black'>{hoa_don.thang}/{hoa_don.nam}</font>", self.styles["Normal_VN"]))
        elements.append(Spacer(1, 5))
        
        # ===== THÔNG TIN KHÁCH HÀNG =====
        elements.append(Paragraph(f"Tên khách hàng: <font color='black'>{khach_hang.ho_ten}</font>", self.customer_style))
        elements.append(Paragraph(f"Địa chỉ: <font color='black'>{khach_hang.dia_chi}</font>", self.customer_style))
        elements.append(Paragraph(f"Mã khách hàng: <font color='black'>{khach_hang.ma_khach_hang}</font> - Số điện thoại: <font color='black'>{khach_hang.so_dien_thoai}</font>", self.customer_style))
        elements.append(Paragraph(f"Mã công tơ: <font color='black'>{khach_hang.ma_cong_to}</font>", self.customer_style))
        elements.append(Spacer(1, 10))
        
        # ===== THÔNG TIN CHỈ SỐ =====
        elements.append(Paragraph("CHỈ SỐ CÔNG TƠ VÀ SẢN LƯỢNG ĐIỆN TIÊU THỤ", self.heading_style))
        chi_so_data = [
            ['CHỈ SỐ CŨ', 'CHỈ SỐ MỚI', 'SẢN LƯỢNG (kWh)'],
            [str(hoa_don.chi_so_dau), str(hoa_don.chi_so_cuoi), str(hoa_don.tieu_thu)]
        ]
        chi_so_table = Table(chi_so_data, colWidths=[130, 130, 130])
        chi_so_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elements.append(chi_so_table)
        elements.append(Spacer(1, 10))
        
        # ===== BẢNG TÍNH TIỀN ĐIỆN =====
        elements.append(Paragraph("CHI TIẾT TIỀN ĐIỆN THEO BẬC THANG", self.heading_style))
        
        # Tính số điện tiêu thụ theo từng bậc thang
        tieu_thu_theo_bac = []
        so_dien_con_lai = hoa_don.tieu_thu
        bac_truoc = 0
        tong_tien_dien = 0  # Tổng tiền điện trước thuế
        
        for i, (dinh_muc, don_gia) in enumerate(bang_gia.bac_thang):
            # Kiểm tra giá trị None cho dinh_muc
            if dinh_muc is None:
                dinh_muc = float('inf')  # Thay thế None bằng vô cùng
            
            # Tính số điện tiêu thụ trong bậc hiện tại
            so_dien_trong_bac = min(dinh_muc - bac_truoc, so_dien_con_lai)
            
            # Chỉ thêm vào danh sách nếu có tiêu thụ trong bậc này
            if so_dien_trong_bac > 0:
                # Tính tiền cho bậc hiện tại
                thanh_tien = so_dien_trong_bac * don_gia
                tong_tien_dien += thanh_tien
                    
                # Thêm vào danh sách
                tieu_thu_theo_bac.append([
                    f"Bậc {i+1}",
                    f"{bac_truoc+1} - {dinh_muc}" if dinh_muc != float('inf') and i < len(bang_gia.bac_thang)-1 else f"Trên {bac_truoc}",
                    f"{so_dien_trong_bac:,}",
                    f"{don_gia:,.0f}",
                    f"{thanh_tien:,.0f}"
                ])
                
                # Cập nhật số điện còn lại
                so_dien_con_lai -= so_dien_trong_bac
            
            # Cập nhật bậc trước
            bac_truoc = dinh_muc
                
            # Nếu hết điện thì dừng
            if so_dien_con_lai <= 0:
                break
        
        # Đảm bảo vat có giá trị
        if bang_gia.vat is None:
            bang_gia.vat = 0.1  # Giá trị VAT mặc định
        
        # Tính tổng tiền, thuế và tổng cộng
        tong_tien_truoc_thue = tong_tien_dien
        tien_thue = int(tong_tien_truoc_thue * bang_gia.vat)
        tong_cong = tong_tien_truoc_thue + tien_thue
        
        # Cập nhật giá trị so_tien cho hóa đơn
        hoa_don.so_tien = tong_cong
        
        # Đổi số thành chữ
        so_tien_bang_chu = self.doc_so_thanh_chu(int(tong_cong))
        
        # Tạo bảng tính tiền
        tien_dien_headers = [
            'BẬC THANG', 'ĐỊNH MỨC (kWh)', 'SẢN LƯỢNG (kWh)', 'ĐƠN GIÁ (VNĐ/kWh)', 'THÀNH TIỀN (VNĐ)'
        ]
        tien_dien_data = [tien_dien_headers] + tieu_thu_theo_bac
        
        # Thêm dòng tổng tiền và thuế
        tien_dien_data.append(['', '', '', 'Tổng tiền điện:', f"{tong_tien_truoc_thue:,.0f}"])
        tien_dien_data.append(['', '', '', f'Thuế GTGT ({int(bang_gia.vat*100)}%):', f"{tien_thue:,.0f}"])
        tien_dien_data.append(['', '', '', 'Tổng cộng:', f"{tong_cong:,.0f}"])
        
        # Tạo bảng
        tien_dien_table = Table(tien_dien_data, colWidths=[80, 95, 80, 110, 125])
        tien_dien_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('SPAN', (0, len(tieu_thu_theo_bac)+1), (2, len(tieu_thu_theo_bac)+1)),  # Span cho dòng tổng tiền
            ('SPAN', (0, len(tieu_thu_theo_bac)+2), (2, len(tieu_thu_theo_bac)+2)),  # Span cho dòng thuế
            ('SPAN', (0, len(tieu_thu_theo_bac)+3), (2, len(tieu_thu_theo_bac)+3)),  # Span cho dòng tổng cộng
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            # Dùng font Roboto-Bold cho dòng tổng cộng
            ('FONTNAME', (3, len(tieu_thu_theo_bac)+3), (4, len(tieu_thu_theo_bac)+3), 'Roboto-Bold'),
            ('FONTSIZE', (3, len(tieu_thu_theo_bac)+3), (4, len(tieu_thu_theo_bac)+3), 10),
        ]))
        elements.append(tien_dien_table)
        
        # Thêm dòng Số tiền bằng chữ vào một bảng riêng biệt
        elements.append(Spacer(1, 5))
        
        # Tạo bảng cho số tiền bằng chữ
        so_tien_bang_chu_data = [['Số tiền bằng chữ:', so_tien_bang_chu]]
        so_tien_bang_chu_table = Table(so_tien_bang_chu_data, colWidths=[120, 370])
        so_tien_bang_chu_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Roboto-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (0, 0), 15),
            ('LEFTPADDING', (1, 0), (1, 0), 15),
        ]))
        elements.append(so_tien_bang_chu_table)
        
        # ===== THÔNG TIN THANH TOÁN =====
        elements.append(Spacer(1, 15))
        
        elements.append(Paragraph(f"Thời hạn thanh toán: Trong vòng 15 ngày kể từ ngày phát hành hóa đơn", self.styles["Normal_VN"]))
        elements.append(Paragraph(f"Hình thức thanh toán: Chuyển khoản, thanh toán trực tuyến hoặc tại các điểm thu hộ", self.styles["Normal_VN"]))
        elements.append(Paragraph(f"Trạng thái thanh toán: {'Đã thanh toán' if hoa_don.da_thanh_toan else 'Chưa thanh toán'}", self.styles["Normal_VN"]))
        
        # ===== KÝ TÊN =====
        ngay_phat_hanh = datetime.datetime.now().strftime("%d/%m/%Y")
        elements.append(Spacer(1, 20))
        
        ky_ten_data = [
            ['KHÁCH HÀNG', '', 'ĐẠI DIỆN ĐƠN VỊ'],
            ['(Ký, ghi rõ họ tên)', '', f'Ngày {ngay_phat_hanh}'],
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            [khach_hang.ho_ten, '', 'CÔNG TY ĐIỆN LỰC VTN VIP']
        ]
        ky_ten_table = Table(ky_ten_data, colWidths=[150, 100, 150])
        ky_ten_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elements.append(ky_ten_table)
        
        # Xuất PDF
        doc.build(elements)
        return file_name

# Hàm tiện ích để tạo hóa đơn trực tiếp từ mã hóa đơn
def tao_hoa_don_pdf(hoa_don, khach_hang, bang_gia, output_dir="exports"):
    """Hàm tiện ích để tạo hóa đơn PDF"""
    generator = HoaDonPDF()
    return generator.tao_hoa_don(hoa_don, khach_hang, bang_gia, output_dir)
