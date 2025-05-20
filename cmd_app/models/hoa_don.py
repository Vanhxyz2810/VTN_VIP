#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

class HoaDon:
    """
    Lớp đại diện cho hóa đơn tiền điện
    """
    
    def __init__(self, ma_hoa_don, ma_khach_hang, thang, nam, chi_so_dau, chi_so_cuoi, 
                 da_thanh_toan=False, ngay_thanh_toan=None, so_tien=None):
        """
        Khởi tạo đối tượng hóa đơn
        
        Args:
            ma_hoa_don (str): Mã định danh hóa đơn
            ma_khach_hang (str): Mã khách hàng liên quan
            thang (int): Tháng của kỳ hóa đơn
            nam (int): Năm của kỳ hóa đơn
            chi_so_dau (int): Chỉ số công tơ đầu kỳ
            chi_so_cuoi (int): Chỉ số công tơ cuối kỳ
            da_thanh_toan (bool): Trạng thái thanh toán
            ngay_thanh_toan (datetime): Ngày thanh toán hóa đơn
            so_tien (float): Số tiền phải thanh toán
        """
        self.ma_hoa_don = ma_hoa_don
        self.ma_khach_hang = ma_khach_hang
        self.thang = thang
        self.nam = nam
        self.chi_so_dau = chi_so_dau
        self.chi_so_cuoi = chi_so_cuoi
        self.da_thanh_toan = da_thanh_toan
        self.ngay_thanh_toan = ngay_thanh_toan
        self.so_tien = so_tien
    
    @property
    def tieu_thu(self):
        """
        Tính số kWh tiêu thụ trong kỳ
        
        Returns:
            int: Số kWh tiêu thụ
        """
        return max(0, self.chi_so_cuoi - self.chi_so_dau)
    
    @property
    def dien_tieu_thu(self):
        """
        Alias cho thuộc tính tieu_thu để đảm bảo tính nhất quán
        
        Returns:
            int: Số kWh tiêu thụ
        """
        return self.tieu_thu
    
    @property
    def tong_tien(self):
        """
        Alias cho thuộc tính so_tien để đảm bảo tính nhất quán
        
        Returns:
            float: Số tiền phải thanh toán
        """
        return self.so_tien
    
    def tinh_tien(self, bang_gia):
        """
        Tính tiền điện dựa trên bảng giá
        
        Args:
            bang_gia (BangGia): Đối tượng bảng giá điện
            
        Returns:
            float: Số tiền phải thanh toán
        """
        self.so_tien = bang_gia.tinh_tien(self.tieu_thu)
        return self.so_tien
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng thành dictionary để lưu trữ
        
        Returns:
            dict: Dictionary chứa thông tin hóa đơn
        """
        return {
            'ma_hoa_don': self.ma_hoa_don,
            'ma_khach_hang': self.ma_khach_hang,
            'thang': self.thang,
            'nam': self.nam,
            'chi_so_dau': self.chi_so_dau,
            'chi_so_cuoi': self.chi_so_cuoi,
            'da_thanh_toan': self.da_thanh_toan,
            'ngay_thanh_toan': self.ngay_thanh_toan.isoformat() if self.ngay_thanh_toan else None,
            'so_tien': self.so_tien
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng hóa đơn từ dictionary
        
        Args:
            data (dict): Dictionary chứa thông tin hóa đơn
            
        Returns:
            HoaDon: Đối tượng hóa đơn mới
        """
        ngay_thanh_toan = None
        if data.get('ngay_thanh_toan'):
            try:
                ngay_thanh_toan = datetime.datetime.fromisoformat(data.get('ngay_thanh_toan'))
            except:
                pass
                
        return cls(
            data.get('ma_hoa_don'),
            data.get('ma_khach_hang'),
            data.get('thang'),
            data.get('nam'),
            data.get('chi_so_dau'),
            data.get('chi_so_cuoi'),
            data.get('da_thanh_toan', False),
            ngay_thanh_toan,
            data.get('so_tien')
        )
    
    def __str__(self):
        """
        Biểu diễn chuỗi của đối tượng hóa đơn
        
        Returns:
            str: Chuỗi mô tả hóa đơn
        """
        trang_thai = "Đã thanh toán" if self.da_thanh_toan else "Chưa thanh toán"
        return f"Hóa đơn: {self.ma_hoa_don} - {self.thang}/{self.nam} - {self.tieu_thu} kWh - {trang_thai}" 