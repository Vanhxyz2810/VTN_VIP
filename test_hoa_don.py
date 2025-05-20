#!/usr/bin/env python
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
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

class HoaDonPDF:
    def __init__(self):
        # Đăng ký font Roboto hỗ trợ tiếng Việt
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'font', 'Roboto-Regular.ttf')
        pdfmetrics.registerFont(TTFont('Roboto', font_path))
        
        # Tạo style mới dùng font Roboto
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Normal_VN', fontName='Roboto', fontSize=10, leading=14))
        self.styles.add(ParagraphStyle(name='Title_VN', fontName='Roboto', fontSize=14, alignment=1, spaceAfter=10))
        self.styles.add(ParagraphStyle(name='Bold_VN', fontName='Roboto', fontSize=10, leading=14, spaceAfter=6))
        self.styles.add(ParagraphStyle(name='Footer_VN', fontName='Roboto', fontSize=8, leading=10, alignment=1))
    
    def doc_so_thanh_chu(self, number):
        """Chuyển đổi số thành chữ tiếng Việt"""
        try:
            # Chuyển đổi số thành chữ bằng num2words
            text = num2words(number, lang='vi')
            # Chuẩn hóa lại chuỗi
            text = text.replace(',', '').replace('-', ' ').title()
            return f"{text} Đồng"
        except:
            # Fallback nếu không thể chuyển đổi
            thousands = number // 1000
            remainder = number % 1000
            if remainder == 0:
                return f"{thousands} Nghìn Đồng"
            else:
                return f"{thousands} Nghìn {remainder} Đồng"

    def tao_hoa_don(self, hoa_don, khach_hang, bang_gia, output_dir="exports"):
        """
        Tạo file PDF hóa đơn điện
        
        Args:
            hoa_don: Đối tượng HoaDon
            khach_hang: Đối tượng KhachHang
            bang_gia: Đối tượng BangGia
            output_dir: Thư mục lưu file PDF
        
        Returns:
            str: Đường dẫn đến file PDF đã tạo
        """
        # Đảm bảo thư mục lưu tồn tại
        os.makedirs(output_dir, exist_ok=True)
        
        # Tạo tên file
        file_name = f"{output_dir}/hoa_don_{hoa_don.ma_hoa_don}.pdf"
        
        # Tạo tài liệu PDF
        doc = SimpleDocTemplate(file_name, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        
        # ===== TIÊU ĐỀ =====
        elements.append(Paragraph("<b>HÓA ĐƠN TIỀN ĐIỆN</b>", self.styles['Title_VN']))
        elements.append(Paragraph("(Bản thể hiện của hóa đơn điện tử)", self.styles['Normal_VN']))
        elements.append(Spacer(1, 5))
        
        # ===== THÔNG TIN CÔNG TY =====
        company_info = """
        <b>CÔNG TY ĐIỆN LỰC VIỆT NAM</b><br/>
        Địa chỉ: Số 11 phố Cửa Bắc, phường Trúc Bạch, quận Ba Đình, Hà Nội<br/>
        Điện thoại: 19009000 - MST: 0100100079
        """
        elements.append(Paragraph(company_info, self.styles["Bold_VN"]))
        elements.append(Spacer(1, 5))
        
        # ===== THÔNG TIN HÓA ĐƠN =====
        invoice_info = f"""
        <b>Mã hóa đơn:</b> {hoa_don.ma_hoa_don}<br/>
        <b>Kỳ hóa đơn:</b> Tháng {hoa_don.thang}/{hoa_don.nam}
        """
        elements.append(Paragraph(invoice_info, self.styles["Normal_VN"]))
        elements.append(Spacer(1, 5))
        
        # ===== THÔNG TIN KHÁCH HÀNG =====
        customer_info = f"""
        <b>Tên khách hàng:</b> {khach_hang.ho_ten}<br/>
        <b>Địa chỉ:</b> {khach_hang.dia_chi}<br/>
        <b>Mã khách hàng:</b> {khach_hang.ma_khach_hang} - <b>Số điện thoại:</b> {khach_hang.so_dien_thoai}<br/>
        <b>Mã công tơ:</b> {khach_hang.ma_cong_to}
        """
        elements.append(Paragraph(customer_info, self.styles["Normal_VN"]))
        elements.append(Spacer(1, 10))
        
        # ===== THÔNG TIN CHỈ SỐ =====
        elements.append(Paragraph("<b>CHỈ SỐ CÔNG TƠ VÀ SẢN LƯỢNG ĐIỆN TIÊU THỤ</b>", self.styles["Bold_VN"]))
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
        elements.append(Paragraph("<b>CHI TIẾT TIỀN ĐIỆN THEO BẬC THANG</b>", self.styles["Bold_VN"]))
        
        # Tính số điện tiêu thụ theo từng bậc thang
        tieu_thu_theo_bac = []
        so_dien_con_lai = hoa_don.tieu_thu
        bac_truoc = 0
        
        for i, (dinh_muc, don_gia) in enumerate(bang_gia.bac_thang):
            # Tính số điện tiêu thụ trong bậc hiện tại
            so_dien_trong_bac = min(dinh_muc - bac_truoc, so_dien_con_lai)
            if so_dien_trong_bac <= 0:
                break
                
            # Tính tiền cho bậc hiện tại
            thanh_tien = so_dien_trong_bac * don_gia
                
            # Thêm vào danh sách
            tieu_thu_theo_bac.append([
                f"Bậc {i+1}",
                f"{bac_truoc+1} - {dinh_muc}" if i < len(bang_gia.bac_thang)-1 else f"Trên {bac_truoc}",
                f"{so_dien_trong_bac}",
                f"{don_gia:,.0f}",
                f"{thanh_tien:,.0f}"
            ])
                
            # Cập nhật số điện còn lại và bậc trước
            so_dien_con_lai -= so_dien_trong_bac
            bac_truoc = dinh_muc
                
            # Nếu hết điện thì dừng
            if so_dien_con_lai <= 0:
                break
        
        # Tính tổng tiền trước thuế
        tong_tien_truoc_thue = int(hoa_don.so_tien / (1 + bang_gia.vat))
        tien_thue = hoa_don.so_tien - tong_tien_truoc_thue
        
        # Tạo bảng tính tiền
        tien_dien_headers = [
            'BẬC THANG', 'ĐỊNH MỨC (kWh)', 'SẢN LƯỢNG (kWh)', 'ĐƠN GIÁ (VNĐ/kWh)', 'THÀNH TIỀN (VNĐ)'
        ]
        tien_dien_data = [tien_dien_headers] + tieu_thu_theo_bac
        
        # Thêm dòng tổng tiền và thuế
        tien_dien_data.append(['', '', '', 'Tổng tiền điện:', f"{tong_tien_truoc_thue:,.0f}"])
        tien_dien_data.append(['', '', '', f'Thuế GTGT ({int(bang_gia.vat*100)}%):', f"{tien_thue:,.0f}"])
        tien_dien_data.append(['', '', '', '<b>Tổng cộng:</b>', f"<b>{hoa_don.so_tien:,.0f}</b>"])
        
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
        ]))
        elements.append(tien_dien_table)
        
        # ===== SỐ TIỀN BẰNG CHỮ =====
        elements.append(Spacer(1, 10))
        so_tien_bang_chu = self.doc_so_thanh_chu(int(hoa_don.so_tien))
        elements.append(Paragraph(f"<b>Số tiền bằng chữ:</b> {so_tien_bang_chu}", self.styles["Normal_VN"]))
        
        # ===== THÔNG TIN THANH TOÁN =====
        elements.append(Spacer(1, 15))
        thanh_toan_info = f"""
        <b>Thời hạn thanh toán:</b> Trong vòng 15 ngày kể từ ngày phát hành hóa đơn<br/>
        <b>Hình thức thanh toán:</b> Chuyển khoản, thanh toán trực tuyến hoặc tại các điểm thu hộ<br/>
        <b>Trạng thái thanh toán:</b> {"Đã thanh toán" if hoa_don.da_thanh_toan else "Chưa thanh toán"}
        """
        elements.append(Paragraph(thanh_toan_info, self.styles["Normal_VN"]))
        
        # ===== KÝ TÊN =====
        ngay_phat_hanh = datetime.datetime.now().strftime("%d/%m/%Y")
        elements.append(Spacer(1, 20))
        
        ky_ten_data = [
            ['KHÁCH HÀNG', '', 'ĐẠI DIỆN ĐƠN VỊ'],
            ['(Ký, ghi rõ họ tên)', '', f'Ngày {ngay_phat_hanh}'],
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            [khach_hang.ho_ten, '', 'CÔNG TY ĐIỆN LỰC VIỆT NAM']
        ]
        ky_ten_table = Table(ky_ten_data, colWidths=[150, 100, 150])
        ky_ten_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elements.append(ky_ten_table)
        
        # ===== FOOTER =====
        elements.append(Spacer(1, 20))
        footer_text = f"""
        Mọi thắc mắc về hóa đơn, vui lòng liên hệ Tổng đài CSKH: 19009000<br/>
        Website: www.evn.com.vn | Mã hóa đơn: {hoa_don.ma_hoa_don}
        """
        elements.append(Paragraph(footer_text, self.styles["Footer_VN"]))
        
        # Xuất PDF
        doc.build(elements)
        return file_name

# Hàm tiện ích để tạo hóa đơn trực tiếp từ mã hóa đơn
def tao_hoa_don_pdf(hoa_don, khach_hang, bang_gia, output_dir="exports"):
    """
    Hàm tiện ích để tạo hóa đơn PDF
    
    Args:
        hoa_don: Đối tượng HoaDon
        khach_hang: Đối tượng KhachHang
        bang_gia: Đối tượng BangGia
        output_dir: Thư mục lưu file PDF
    
    Returns:
        str: Đường dẫn đến file PDF đã tạo
    """
    generator = HoaDonPDF()
    return generator.tao_hoa_don(hoa_don, khach_hang, bang_gia, output_dir)

# Nếu chạy trực tiếp file này
if __name__ == "__main__":
    # Import các lớp để demo
    import sys
    import os
    
    # Thêm thư mục gốc vào đường dẫn
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from cmd_app.models.khach_hang import KhachHang
    from cmd_app.models.hoa_don import HoaDon
    from cmd_app.models.bang_gia import BangGia
    
    # Tạo dữ liệu mẫu
    khach_hang = KhachHang(
        ma_khach_hang="KH123456",
        ho_ten="Nguyễn Văn A",
        dia_chi="Ấp 1, xã Trung Ngãi, huyện Vũng Liêm, tỉnh Vĩnh Long",
        so_dien_thoai="0987654321",
        ma_cong_to="CT123456"
    )
    
    bang_gia = BangGia(
        ma_bang_gia="BG123456",
        ngay_ap_dung="01/01/2023",
        bac_thang=[
            (50, 1678),     # Bậc 1: 0-50 kWh
            (100, 1734),    # Bậc 2: 51-100 kWh
            (200, 2014),    # Bậc 3: 101-200 kWh
            (300, 2536),    # Bậc 4: 201-300 kWh
            (400, 2834),    # Bậc 5: 301-400 kWh
            (float('inf'), 2927)  # Bậc 6: Trên 400 kWh
        ]
    )
    
    hoa_don = HoaDon(
        ma_hoa_don="HD123456",
        ma_khach_hang="KH123456",
        thang=1,
        nam=2023,
        chi_so_dau=12345,
        chi_so_cuoi=12617,
        da_thanh_toan=False,
        ngay_thanh_toan=None,
        so_tien=562903
    )
    
    # Tạo hóa đơn PDF
    generator = HoaDonPDF()
    file_path = generator.tao_hoa_don(hoa_don, khach_hang, bang_gia)
    print(f"✅ Đã tạo hóa đơn tại: {file_path}")
