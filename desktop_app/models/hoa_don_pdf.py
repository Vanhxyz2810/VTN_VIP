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
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
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

# Màu chủ đạo theo logo VTN
VTN_YELLOW = colors.Color(1, 0.7, 0, 1)         # Màu vàng #FFB300
VTN_ORANGE = colors.Color(1, 0.6, 0, 1)         # Màu cam #FF9800
VTN_LIGHT_YELLOW = colors.Color(1, 0.98, 0.9, 1) # Màu vàng nhạt #FFFDE7
VTN_BACKGROUND = colors.Color(0.97, 0.97, 0.97, 1) # Màu nền xám nhạt
VTN_TEXT = colors.Color(0.13, 0.13, 0.13, 1)     # Màu chữ #212121

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
        
        # Đặt màu nền trắng cho toàn bộ trang
        canvas.saveState()
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)
        
        # Tạo viền màu vàng cam ở trên
        canvas.setFillColor(VTN_ORANGE)
        canvas.rect(0, height-40, width, 40, fill=1, stroke=0)
        
        # Tạo viền màu vàng ở dưới
        canvas.setFillColor(VTN_YELLOW)
        canvas.rect(0, 0, width, 15, fill=1, stroke=0)
        
        # Thêm viền mờ ở góc
        canvas.setFillColor(VTN_LIGHT_YELLOW)
        canvas.setFillAlpha(0.5)
        
        # Viền trang trí góc trên phải
        path = canvas.beginPath()
        path.moveTo(width-100, height)
        path.lineTo(width, height)
        path.lineTo(width, height-100)
        path.lineTo(width-100, height)
        canvas.drawPath(path, fill=1, stroke=0)
        
        # Viền trang trí góc dưới trái
        path = canvas.beginPath()
        path.moveTo(0, 100)
        path.lineTo(0, 0)
        path.lineTo(100, 0)
        path.lineTo(0, 100)
        canvas.drawPath(path, fill=1, stroke=0)
        
        # Thêm ngày tháng ở góc trên phải
        canvas.setFillAlpha(1)
        canvas.setFillColor(colors.white)
        canvas.setFont("Roboto", 9)
        
        # Format ngày tháng
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        canvas.drawRightString(width-25, height-25, f"Ngày: {today}")
        
        # Thêm watermark mờ
        canvas.saveState()
        canvas.setFont("Roboto-Bold", 50)
        canvas.setFillColor(VTN_LIGHT_YELLOW)
        canvas.setFillAlpha(0.1)
        canvas.translate(width/2, height/2)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "VTN VIP")
        canvas.restoreState()
        
        # Thêm footer
        canvas.setFont("Roboto", 9)
        canvas.setFillColor(VTN_TEXT)
        canvas.drawCentredString(width/2, 30, "Cảm ơn quý khách đã sử dụng dịch vụ")
        canvas.drawCentredString(width/2, 20, "Hotline hỗ trợ khách hàng: 19009000")
        
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
        
        # Style cho tiêu đề chính - màu trắng
        self.title_style = ParagraphStyle(
            name='Title_Style',
            fontName='Roboto-Bold',
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.white
        )
        
        # Style cho subtitle - màu trắng và căn giữa
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
            textColor=VTN_ORANGE,
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Style cho heading phụ
        self.subheading_style = ParagraphStyle(
            name='Subheading_Style',
            fontName='Roboto-Bold',
            fontSize=11,
            leading=14,
            textColor=VTN_YELLOW,
            spaceBefore=10,
            spaceAfter=8
        )
        
        # Style cho company text đậm - màu cam
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
            textColor=VTN_YELLOW
        )
        
        # Style cho giá trị thông tin - màu đen đậm
        self.value_style = ParagraphStyle(
            name='Value_Style',
            fontName='Roboto-Bold',
            fontSize=10,
            leading=14,
            textColor=VTN_TEXT
        )
        
        # Style cho summary - màu cam, đậm, cỡ lớn
        self.summary_style = ParagraphStyle(
            name='Summary_Style',
            fontName='Roboto-Bold',
            fontSize=13,
            leading=16,
            alignment=TA_RIGHT,
            textColor=VTN_ORANGE
        )
    
    def doc_so_thanh_chu(self, number):
        """Chuyển đổi số thành chữ tiếng Việt"""
        try:
            text = num2words(number, lang='vi')
            text = text.replace(',', '').replace('-', ' ').title()
            return f"{text} Đồng"
        except:
            thousands = number // 1000
            remainder = number % 1000
            if remainder == 0:
                return f"{thousands} Nghìn Đồng"
            else:
                return f"{thousands} Nghìn {remainder} Đồng"

    def tao_hoa_don(self, hoa_don, khach_hang, bang_gia, output_dir="exports"):
        """Tạo file PDF hóa đơn điện"""
        # Đảm bảo thư mục lưu tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Tạo tên file
        file_name = f"{output_dir}/hoa_don_{hoa_don.ma_hoa_don}.pdf"
        
        # Tạo tài liệu PDF với nền màu trắng và trang trí
        doc = HoaDonPDFTemplate(file_name, pagesize=A4, rightMargin=25, leftMargin=25, topMargin=70, bottomMargin=45)
        elements = []
        
        # Tìm đường dẫn logo
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, 'imgs', '@vtn_vip.png')
        
        # Khoảng cách
        elements.append(Spacer(1, 10))
        
        # ===== HEADER: LOGO VÀ TIÊU ĐỀ =====
        if os.path.exists(logo_path):
            # Chuẩn bị logo
            logo = Image(logo_path, width=90, height=45, hAlign='LEFT')
            
            # Chuẩn bị tiêu đề
            title = Paragraph("HÓA ĐƠN TIỀN ĐIỆN", self.title_style)
            subtitle = Paragraph("(Bản thể hiện hóa đơn điện tử)", self.subtitle_style)
            
            # Tạo bảng header với logo bên trái, tiêu đề bên phải
            header_data = [
                [logo, title],
                ['', subtitle]
            ]
            header_table = Table(header_data, colWidths=[100, 380])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Logo căn trái
                ('ALIGN', (1, 0), (1, -1), 'CENTER'), # Tiêu đề căn giữa
                ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),# Căn giữa theo chiều dọc
                ('SPAN', (0, 0), (0, 1)),             # Gộp hai dòng cho logo
                ('BACKGROUND', (1, 0), (1, 1), VTN_ORANGE),  # Nền màu cho tiêu đề
                ('LEFTPADDING', (0, 0), (0, 0), 2),   # Padding bên trái cho logo
                ('RIGHTPADDING', (0, 0), (0, 0), 5),  # Padding bên phải cho logo
                ('BOTTOMPADDING', (0, 0), (1, 1), 10),# Padding dưới cho tất cả
                ('TOPPADDING', (0, 0), (1, 1), 10),   # Padding trên cho tất cả
                ('ROUNDEDCORNERS', [5, 5, 5, 5]),     # Bo góc cho bảng
            ]))
            elements.append(header_table)
        else:
            # Nếu không có logo, chỉ thêm tiêu đề
            title_table = Table([[Paragraph("HÓA ĐƠN TIỀN ĐIỆN", self.title_style)], 
                               [Paragraph("(Bản thể hiện hóa đơn điện tử)", self.subtitle_style)]], 
                              colWidths=[480])
            
            title_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 0), (-1, -1), VTN_ORANGE),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ]))
            elements.append(title_table)
        
        elements.append(Spacer(1, 15))
        
        # ===== THÔNG TIN CÔNG TY VÀ HÓA ĐƠN =====
        # Tạo bảng thông tin công ty ở bên trái và thông tin hóa đơn ở bên phải
        company_info = [
            [Paragraph("CÔNG TY ĐIỆN LỰC VTN VIP", self.company_style)],
            [Paragraph("Địa chỉ: <font color='#212121'>Số 11 Cửa Bắc, Trúc Bạch, Ba Đình, Hà Nội</font>", self.customer_label_style)],
            [Paragraph("Điện thoại: <font color='#212121'>19009000</font>", self.customer_label_style)],
            [Paragraph("MST: <font color='#212121'>0100100079</font>", self.customer_label_style)]
        ]
        
        bill_info = [
            [Paragraph(f"MÃ HÓA ĐƠN: <font color='#FF9800'>{hoa_don.ma_hoa_don}</font>", self.value_style)],
            [Paragraph(f"Ngày lập: <font color='#212121'>{datetime.datetime.now().strftime('%d/%m/%Y')}</font>", self.customer_label_style)],
            [Paragraph(f"Kỳ thanh toán: <font color='#212121'>Tháng {hoa_don.thang}/{hoa_don.nam}</font>", self.customer_label_style)],
            [Paragraph(f"Trạng thái: <font color='{'green' if hoa_don.da_thanh_toan else 'red'}'>{('Đã thanh toán') if hoa_don.da_thanh_toan else ('Chưa thanh toán')}</font>", self.customer_label_style)]
        ]
        
        header_table = Table(
            [[
                Table(company_info, colWidths=[240]),
                Table(bill_info, colWidths=[240])
            ]],
            colWidths=[240, 240]
        )
        
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (1, 0), 'TOP'),
            ('LEFTPADDING', (0, 0), (1, 0), 0),
            ('RIGHTPADDING', (0, 0), (1, 0), 0),
            ('TOPPADDING', (0, 0), (1, 0), 0),
            ('BOTTOMPADDING', (0, 0), (1, 0), 0),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # ===== VIỀN NGĂN CÁCH =====
        separator = Table([['']], colWidths=[480], rowHeights=[2])
        separator.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), VTN_YELLOW),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(separator)
        elements.append(Spacer(1, 10))
        
        # ===== THÔNG TIN KHÁCH HÀNG =====
        elements.append(Paragraph("THÔNG TIN KHÁCH HÀNG", self.heading_style))
        
        # Tạo bảng thông tin khách hàng đẹp với nền màu nhẹ
        customer_data = [
            [Paragraph("Tên khách hàng:", self.customer_label_style), 
             Paragraph(f"<b>{khach_hang.ho_ten}</b>", self.value_style)],
            [Paragraph("Địa chỉ:", self.customer_label_style), 
             Paragraph(f"{khach_hang.dia_chi}", self.value_style)],
            [Paragraph("Mã khách hàng:", self.customer_label_style), 
             Paragraph(f"{khach_hang.ma_khach_hang}", self.value_style)],
            [Paragraph("Số điện thoại:", self.customer_label_style), 
             Paragraph(f"{khach_hang.so_dien_thoai}", self.value_style)],
            [Paragraph("Mã công tơ:", self.customer_label_style), 
             Paragraph(f"{khach_hang.ma_cong_to}", self.value_style)]
        ]
        
        customer_table = Table(customer_data, colWidths=[120, 360])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), VTN_LIGHT_YELLOW),
            ('BACKGROUND', (0, 0), (0, -1), VTN_YELLOW),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Roboto-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        
        elements.append(customer_table)
        elements.append(Spacer(1, 15))
        
        # ===== THÔNG TIN CHỈ SỐ =====
        elements.append(Paragraph("CHỈ SỐ CÔNG TƠ VÀ SẢN LƯỢNG ĐIỆN TIÊU THỤ", self.heading_style))
        
        chi_so_data = [
            ['CHỈ SỐ ĐẦU KỲ', 'CHỈ SỐ CUỐI KỲ', 'SẢN LƯỢNG (kWh)'],
            [str(hoa_don.chi_so_dau), str(hoa_don.chi_so_cuoi), str(hoa_don.tieu_thu)]
        ]
        
        chi_so_table = Table(chi_so_data, colWidths=[160, 160, 160])
        chi_so_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), VTN_ORANGE),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTNAME', (0, 1), (-1, 1), 'Roboto-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
        ]))
        
        elements.append(chi_so_table)
        elements.append(Spacer(1, 15))
        
        # ===== BẢNG TÍNH TIỀN ĐIỆN =====
        elements.append(Paragraph("CHI TIẾT TIỀN ĐIỆN THEO BẬC THANG", self.heading_style))
        
        # Tính số điện tiêu thụ theo từng bậc thang
        tieu_thu_theo_bac = []
        so_dien_con_lai = hoa_don.tieu_thu
        bac_truoc = 0
        
        for i, (dinh_muc, don_gia) in enumerate(bang_gia.bac_thang):
            # Tính số điện tiêu thụ trong bậc hiện tại
            so_dien_trong_bac = min(dinh_muc - bac_truoc, so_dien_con_lai)
            if so_dien_trong_bac <= 0:
                break
            
            # Tính tiền điện trong bậc hiện tại
            tien_dien = so_dien_trong_bac * don_gia
            
            # Thêm vào danh sách
            tieu_thu_theo_bac.append({
                'bac': i + 1,
                'tu_den': f"{bac_truoc + 1} - {dinh_muc}",
                'so_dien': so_dien_trong_bac,
                'don_gia': don_gia,
                'thanh_tien': tien_dien
            })
            
            # Cập nhật số điện còn lại và bậc trước
            so_dien_con_lai -= so_dien_trong_bac
            bac_truoc = dinh_muc
            
            if so_dien_con_lai <= 0:
                break
        
        # Nếu vẫn còn điện chưa tính (vượt quá bậc cao nhất)
        if so_dien_con_lai > 0 and len(bang_gia.bac_thang) > 0:
            # Lấy đơn giá của bậc cao nhất
            _, don_gia_cao_nhat = bang_gia.bac_thang[-1]
            tien_dien = so_dien_con_lai * don_gia_cao_nhat
            
            # Thêm vào danh sách
            tieu_thu_theo_bac.append({
                'bac': len(bang_gia.bac_thang) + 1,
                'tu_den': f"> {bac_truoc}",
                'so_dien': so_dien_con_lai,
                'don_gia': don_gia_cao_nhat,
                'thanh_tien': tien_dien
            })
        
        # Tạo dữ liệu cho bảng tính tiền điện
        tien_dien_data = [
            ['BẬC', 'MỨC TIÊU THỤ (kWh)', 'SỐ LƯỢNG (kWh)', 'ĐƠN GIÁ (đ/kWh)', 'THÀNH TIỀN (đ)']
        ]
        
        tong_tien = 0
        for bac in tieu_thu_theo_bac:
            tien_dien_data.append([
                str(bac['bac']),
                bac['tu_den'],
                str(bac['so_dien']),
                f"{bac['don_gia']:,.0f}".replace(',', '.'),
                f"{bac['thanh_tien']:,.0f}".replace(',', '.')
            ])
            tong_tien += bac['thanh_tien']
        
        # Thêm dòng tổng tiền
        tien_dien_data.append([
            '', 'TỔNG CỘNG', str(hoa_don.tieu_thu),
            '', f"{tong_tien:,.0f}".replace(',', '.')
        ])
        
        # Tạo bảng tính tiền điện
        tien_dien_table = Table(tien_dien_data, colWidths=[40, 120, 80, 110, 130])
        tien_dien_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 1, VTN_ORANGE),
            ('BACKGROUND', (0, 0), (-1, 0), VTN_ORANGE),
            ('BACKGROUND', (0, -1), (-1, -1), VTN_LIGHT_YELLOW),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -2), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Roboto-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('SPAN', (0, -1), (1, -1)),
            ('SPAN', (3, -1), (3, -1)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
        ]))
        
        elements.append(tien_dien_table)
        elements.append(Spacer(1, 15))
        
        # ===== TỔNG CỘNG =====
        elements.append(Paragraph("TỔNG CỘNG TIỀN ĐIỆN", self.heading_style))
        
        # Thêm các khoản phụ thu, thuế, v.v. nếu có
        thue_vat = tong_tien * 0.1  # Thuế VAT 10%
        tong_cong = tong_tien + thue_vat
        
        tong_cong_data = [
            ['KHOẢN MỤC', 'THÀNH TIỀN (đ)'],
            ['Tiền điện', f"{tong_tien:,.0f}".replace(',', '.')],
            ['Thuế GTGT (10%)', f"{thue_vat:,.0f}".replace(',', '.')],
            ['TỔNG CỘNG', f"{tong_cong:,.0f}".replace(',', '.')]
        ]
        
        # Hiển thị số tiền bằng chữ
        so_tien_bang_chu = self.doc_so_thanh_chu(int(tong_cong))
        
        # Tạo bảng tổng cộng
        tong_cong_table = Table(tong_cong_data, colWidths=[240, 240])
        tong_cong_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), VTN_ORANGE),
            ('BACKGROUND', (0, -1), (-1, -1), VTN_YELLOW),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Roboto-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, VTN_YELLOW),
        ]))
        
        elements.append(tong_cong_table)
        elements.append(Spacer(1, 10))
        
        # Hiển thị số tiền bằng chữ
        elements.append(Paragraph(f"<i>Bằng chữ: <b>{so_tien_bang_chu}</b></i>", self.value_style))
        
        # Biên nhận
        elements.append(Spacer(1, 25))
        
        # Tạo bảng chữ ký
        if hoa_don.da_thanh_toan:
            signature_data = [
                ['NGƯỜI LẬP HÓA ĐƠN', 'KHÁCH HÀNG'],
                ['(Ký, ghi rõ họ tên)', '(Ký, ghi rõ họ tên)'],
                ['', ''],
                ['', ''],
                ['', ''],
                ['VTN VIP', khach_hang.ho_ten]
            ]
        else:
            signature_data = [
                ['NGƯỜI LẬP HÓA ĐƠN', ''],
                ['(Ký, ghi rõ họ tên)', ''],
                ['', ''],
                ['', ''],
                ['', ''],
                ['VTN VIP', '']
            ]
        
        signature_table = Table(signature_data, colWidths=[240, 240])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Roboto-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Roboto-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(signature_table)
        
        # Build the PDF
        doc.build(elements)
        return file_name

# Hàm tiện ích để tạo hóa đơn trực tiếp từ mã hóa đơn
def tao_hoa_don_pdf(hoa_don, khach_hang, bang_gia, output_dir="exports"):
    """Hàm tiện ích để tạo hóa đơn PDF"""
    generator = HoaDonPDF()
    return generator.tao_hoa_don(hoa_don, khach_hang, bang_gia, output_dir) 