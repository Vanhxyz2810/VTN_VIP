#!/usr/bin/env python
# -*- coding: utf-8 -*-

class KhachHang:
    """
    Lớp đại diện cho thông tin khách hàng
    """
    
    def __init__(self, ma_khach_hang, ho_ten, dia_chi, so_dien_thoai, ma_cong_to):
        """
        Khởi tạo đối tượng khách hàng
        
        Args:
            ma_khach_hang (str): Mã định danh khách hàng
            ho_ten (str): Họ tên khách hàng
            dia_chi (str): Địa chỉ khách hàng
            so_dien_thoai (str): Số điện thoại liên hệ
            ma_cong_to (str): Mã số công tơ điện
        """
        self.ma_khach_hang = ma_khach_hang
        self.ho_ten = ho_ten
        self.dia_chi = dia_chi
        self.so_dien_thoai = so_dien_thoai
        self.ma_cong_to = ma_cong_to
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng thành dictionary để lưu trữ
        
        Returns:
            dict: Dictionary chứa thông tin khách hàng
        """
        return {
            'ma_khach_hang': self.ma_khach_hang,
            'ho_ten': self.ho_ten,
            'dia_chi': self.dia_chi,
            'so_dien_thoai': self.so_dien_thoai,
            'ma_cong_to': self.ma_cong_to
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng khách hàng từ dictionary
        
        Args:
            data (dict): Dictionary chứa thông tin khách hàng
            
        Returns:
            KhachHang: Đối tượng khách hàng mới
        """
        return cls(
            data.get('ma_khach_hang'),
            data.get('ho_ten'),
            data.get('dia_chi'),
            data.get('so_dien_thoai'),
            data.get('ma_cong_to')
        )
    
    def __str__(self):
        """
        Biểu diễn chuỗi của đối tượng khách hàng
        
        Returns:
            str: Chuỗi mô tả khách hàng
        """
        return f"Khách hàng: {self.ho_ten} (Mã: {self.ma_khach_hang})" 