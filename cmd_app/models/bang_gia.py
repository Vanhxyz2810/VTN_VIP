#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

class BangGia:
    """
    Lớp đại diện cho bảng giá điện theo bậc thang
    """
    
    def __init__(self, ma_bang_gia, ngay_ap_dung, bac_thang=None):
        """
        Khởi tạo đối tượng bảng giá điện
        
        Args:
            ma_bang_gia (str): Mã định danh bảng giá
            ngay_ap_dung (datetime): Ngày bắt đầu áp dụng bảng giá
            bac_thang (list): Danh sách bậc thang giá, mỗi phần tử là tuple (kWh_max, don_gia)
                              với kWh_max là giới hạn trên của bậc thang (số kWh tối đa),
                              don_gia là đơn giá cho bậc thang đó (VND/kWh)
        """
        self.ma_bang_gia = ma_bang_gia
        self.ngay_ap_dung = ngay_ap_dung
        
        # Nếu không có dữ liệu bậc thang, sử dụng giá mặc định
        if bac_thang is None:
            # Bậc thang mặc định (cập nhật mới nhất 2023)
            # (kWh_max, don_gia)
            self.bac_thang = [
                (50, 1985),     # Bậc 1: 0-50kWh
                (100, 2051),    # Bậc 2: 51-100kWh
                (200, 2381),    # Bậc 3: 101-200kWh
                (300, 2999),    # Bậc 4: 201-300kWh 
                (400, 3351),    # Bậc 5: 301-400kWh
                (float('inf'), 3461)  # Bậc 6: >400kWh
            ]
        else:
            # Đảm bảo không có giá trị None trong bậc thang
            self.bac_thang = []
            for kwh_max, don_gia in bac_thang:
                if kwh_max is None:
                    self.bac_thang.append((float('inf'), don_gia))
                else:
                    self.bac_thang.append((kwh_max, don_gia))
            
        # Các thuộc tính bổ sung
        self.min_values = self._calculate_min_values()
        self.max_values = self._calculate_max_values()
        self.gia_values = self._calculate_gia_values()
        
        # Thuế VAT, mặc định 10%
        self.vat = 0.1
        
        # Trạng thái đang áp dụng
        self.trang_thai = False
    
    def _calculate_min_values(self):
        """
        Tính giá trị tối thiểu cho mỗi bậc thang
        
        Returns:
            list: Danh sách các giá trị tối thiểu
        """
        min_values = []
        for i, (kwh_max, _) in enumerate(self.bac_thang):
            if i == 0:
                min_values.append(0)
            else:
                # Giá trị tối thiểu của bậc này là giá trị tối đa của bậc trước + 1
                prev_max = self.bac_thang[i-1][0]
                # Xử lý nếu prev_max là None
                if prev_max is None:
                    prev_max = float('inf')
                min_values.append(prev_max + 1)
        return min_values
    
    def _calculate_max_values(self):
        """
        Lấy giá trị tối đa cho mỗi bậc thang
        
        Returns:
            list: Danh sách các giá trị tối đa
        """
        return [float('inf') if kwh_max is None else kwh_max for kwh_max, _ in self.bac_thang]
    
    def _calculate_gia_values(self):
        """
        Lấy giá tiền cho mỗi bậc thang
        
        Returns:
            list: Danh sách các giá tiền
        """
        return [gia for _, gia in self.bac_thang]
    
    def tinh_tien(self, so_kwh):
        """
        Tính tiền điện dựa trên số kWh tiêu thụ
        
        Args:
            so_kwh (int): Số kWh tiêu thụ
            
        Returns:
            float: Số tiền phải thanh toán (đã bao gồm VAT)
        """
        tien_dien = 0
        kwh_con_lai = so_kwh
        bac_hien_tai = 0
        kwh_bac_truoc = 0
        
        for kWh_max, don_gia in self.bac_thang:
            # Xử lý nếu kWh_max là None (vô cùng)
            if kWh_max is None:
                kWh_max = float('inf')
                
            # Số kWh của bậc hiện tại
            kwh_bac_hien_tai = min(kWh_max - kwh_bac_truoc, kwh_con_lai)
            
            # Kiểm tra nếu không còn kWh để tính
            if kwh_bac_hien_tai <= 0:
                break
                
            # Tính tiền cho bậc hiện tại
            tien_dien += kwh_bac_hien_tai * don_gia
            
            # Giảm số kWh còn lại và cập nhật bậc
            kwh_con_lai -= kwh_bac_hien_tai
            kwh_bac_truoc = kWh_max
            bac_hien_tai += 1
            
            # Kiểm tra nếu đã tính hết số kWh
            if kwh_con_lai <= 0:
                break
        
        # Tính tổng tiền sau khi thêm VAT
        tong_tien = tien_dien * (1 + self.vat)
        return round(tong_tien, 2)
    
    def to_dict(self):
        """
        Chuyển đổi đối tượng thành dictionary để lưu trữ
        
        Returns:
            dict: Dictionary chứa thông tin bảng giá
        """
        return {
            'ma_bang_gia': self.ma_bang_gia,
            'ngay_ap_dung': self.ngay_ap_dung.isoformat() if self.ngay_ap_dung else None,
            'bac_thang': self.bac_thang,
            'vat': self.vat,
            'trang_thai': self.trang_thai
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đối tượng bảng giá từ dictionary
        
        Args:
            data (dict): Dictionary chứa thông tin bảng giá
            
        Returns:
            BangGia: Đối tượng bảng giá mới
        """
        ngay_ap_dung = None
        if data.get('ngay_ap_dung'):
            try:
                ngay_ap_dung = datetime.datetime.fromisoformat(data.get('ngay_ap_dung'))
            except:
                pass
        
        # Lấy bậc thang từ dữ liệu và chuẩn hóa
        bac_thang = data.get('bac_thang')
        if bac_thang:
            # Chuẩn hóa bậc thang: thay thế None bằng float('inf')
            bac_thang_normalized = []
            for item in bac_thang:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    kwh_max, don_gia = item
                    if kwh_max is None:
                        bac_thang_normalized.append((float('inf'), don_gia))
                    else:
                        bac_thang_normalized.append((kwh_max, don_gia))
                else:
                    # Nếu định dạng không đúng, bỏ qua phần tử này
                    continue
            bac_thang = bac_thang_normalized
                
        instance = cls(
            data.get('ma_bang_gia'),
            ngay_ap_dung,
            bac_thang
        )
        
        if 'vat' in data:
            instance.vat = data.get('vat')
        
        if 'trang_thai' in data:
            instance.trang_thai = data.get('trang_thai')
            
        return instance 