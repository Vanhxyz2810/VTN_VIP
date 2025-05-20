#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
from models.khach_hang import KhachHang
from models.hoa_don import HoaDon
from models.bang_gia import BangGia

class DatabaseHandler:
    """
    Lớp xử lý lưu trữ và truy xuất dữ liệu cho ứng dụng
    """
    
    def __init__(self, data_dir="../data"):
        """
        Khởi tạo DatabaseHandler
        
        Args:
            data_dir (str): Thư mục lưu trữ dữ liệu
        """
        self.data_dir = data_dir
        self.khach_hang_file = os.path.join(data_dir, "khach_hang.json")
        self.hoa_don_file = os.path.join(data_dir, "hoa_don.json")
        self.bang_gia_file = os.path.join(data_dir, "bang_gia.json")
        
        # Đảm bảo thư mục dữ liệu tồn tại
        self._ensure_data_dir()
        
        # Khởi tạo dữ liệu nếu chưa có
        self._init_data_files()
    
    def _ensure_data_dir(self):
        """Đảm bảo thư mục dữ liệu tồn tại"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _init_data_files(self):
        """Khởi tạo các file dữ liệu nếu chưa tồn tại"""
        # Khởi tạo file khách hàng
        if not os.path.exists(self.khach_hang_file):
            with open(self.khach_hang_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        
        # Khởi tạo file hóa đơn
        if not os.path.exists(self.hoa_don_file):
            with open(self.hoa_don_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        
        # Khởi tạo file bảng giá với bảng giá mặc định
        if not os.path.exists(self.bang_gia_file):
            bang_gia_mac_dinh = BangGia(
                ma_bang_gia="BG001",
                ngay_ap_dung=datetime.datetime.now()
            )
            with open(self.bang_gia_file, 'w', encoding='utf-8') as f:
                json.dump([bang_gia_mac_dinh.to_dict()], f, ensure_ascii=False, indent=4)
    
    # Các phương thức quản lý khách hàng
    def get_all_khach_hang(self):
        """
        Lấy tất cả khách hàng
        
        Returns:
            list: Danh sách các đối tượng KhachHang
        """
        try:
            with open(self.khach_hang_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [KhachHang.from_dict(item) for item in data]
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu khách hàng: {e}")
            return []
    
    def get_khach_hang(self, ma_khach_hang):
        """
        Lấy thông tin một khách hàng theo mã
        
        Args:
            ma_khach_hang (str): Mã khách hàng cần tìm
            
        Returns:
            KhachHang: Đối tượng khách hàng hoặc None nếu không tìm thấy
        """
        for kh in self.get_all_khach_hang():
            if kh.ma_khach_hang == ma_khach_hang:
                return kh
        return None
    
    def add_khach_hang(self, khach_hang):
        """
        Thêm khách hàng mới
        
        Args:
            khach_hang (KhachHang): Đối tượng khách hàng cần thêm
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            khach_hang_list = self.get_all_khach_hang()
            
            # Kiểm tra mã khách hàng đã tồn tại chưa
            for kh in khach_hang_list:
                if kh.ma_khach_hang == khach_hang.ma_khach_hang:
                    return False
            
            khach_hang_list.append(khach_hang)
            
            with open(self.khach_hang_file, 'w', encoding='utf-8') as f:
                json.dump([kh.to_dict() for kh in khach_hang_list], f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Lỗi khi thêm khách hàng: {e}")
            return False
    
    def update_khach_hang(self, khach_hang):
        """
        Cập nhật thông tin khách hàng
        
        Args:
            khach_hang (KhachHang): Đối tượng khách hàng với thông tin mới
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            khach_hang_list = self.get_all_khach_hang()
            
            for i, kh in enumerate(khach_hang_list):
                if kh.ma_khach_hang == khach_hang.ma_khach_hang:
                    khach_hang_list[i] = khach_hang
                    
                    with open(self.khach_hang_file, 'w', encoding='utf-8') as f:
                        json.dump([kh.to_dict() for kh in khach_hang_list], f, ensure_ascii=False, indent=4)
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Lỗi khi cập nhật khách hàng: {e}")
            return False
    
    def delete_khach_hang(self, ma_khach_hang):
        """
        Xóa khách hàng theo mã
        
        Args:
            ma_khach_hang (str): Mã khách hàng cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            khach_hang_list = self.get_all_khach_hang()
            
            for i, kh in enumerate(khach_hang_list):
                if kh.ma_khach_hang == ma_khach_hang:
                    del khach_hang_list[i]
                    
                    with open(self.khach_hang_file, 'w', encoding='utf-8') as f:
                        json.dump([kh.to_dict() for kh in khach_hang_list], f, ensure_ascii=False, indent=4)
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Lỗi khi xóa khách hàng: {e}")
            return False
    
    # Các phương thức quản lý hóa đơn
    def get_all_hoa_don(self):
        """
        Lấy tất cả hóa đơn
        
        Returns:
            list: Danh sách các đối tượng HoaDon
        """
        try:
            with open(self.hoa_don_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [HoaDon.from_dict(item) for item in data]
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu hóa đơn: {e}")
            return []
    
    def get_hoa_don(self, ma_hoa_don):
        """
        Lấy thông tin một hóa đơn theo mã
        
        Args:
            ma_hoa_don (str): Mã hóa đơn cần tìm
            
        Returns:
            HoaDon: Đối tượng hóa đơn hoặc None nếu không tìm thấy
        """
        for hd in self.get_all_hoa_don():
            if hd.ma_hoa_don == ma_hoa_don:
                return hd
        return None
    
    def add_hoa_don(self, hoa_don):
        """
        Thêm hóa đơn mới
        
        Args:
            hoa_don (HoaDon): Đối tượng hóa đơn cần thêm
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            hoa_don_list = self.get_all_hoa_don()
            
            # Kiểm tra mã hóa đơn đã tồn tại chưa
            for hd in hoa_don_list:
                if hd.ma_hoa_don == hoa_don.ma_hoa_don:
                    return False
            
            hoa_don_list.append(hoa_don)
            
            with open(self.hoa_don_file, 'w', encoding='utf-8') as f:
                json.dump([hd.to_dict() for hd in hoa_don_list], f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Lỗi khi thêm hóa đơn: {e}")
            return False
    
    def update_hoa_don(self, hoa_don):
        """
        Cập nhật thông tin hóa đơn
        
        Args:
            hoa_don (HoaDon): Đối tượng hóa đơn với thông tin mới
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            hoa_don_list = self.get_all_hoa_don()
            
            for i, hd in enumerate(hoa_don_list):
                if hd.ma_hoa_don == hoa_don.ma_hoa_don:
                    hoa_don_list[i] = hoa_don
                    
                    with open(self.hoa_don_file, 'w', encoding='utf-8') as f:
                        json.dump([hd.to_dict() for hd in hoa_don_list], f, ensure_ascii=False, indent=4)
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Lỗi khi cập nhật hóa đơn: {e}")
            return False
    
    def delete_hoa_don(self, ma_hoa_don):
        """
        Xóa hóa đơn theo mã
        
        Args:
            ma_hoa_don (str): Mã hóa đơn cần xóa
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            hoa_don_list = self.get_all_hoa_don()
            
            for i, hd in enumerate(hoa_don_list):
                if hd.ma_hoa_don == ma_hoa_don:
                    del hoa_don_list[i]
                    
                    with open(self.hoa_don_file, 'w', encoding='utf-8') as f:
                        json.dump([hd.to_dict() for hd in hoa_don_list], f, ensure_ascii=False, indent=4)
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Lỗi khi xóa hóa đơn: {e}")
            return False
    
    # Các phương thức quản lý bảng giá
    def get_all_bang_gia(self):
        """
        Lấy tất cả bảng giá
        
        Returns:
            list: Danh sách các đối tượng BangGia
        """
        try:
            with open(self.bang_gia_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [BangGia.from_dict(item) for item in data]
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu bảng giá: {e}")
            return []
    
    def get_bang_gia(self, ma_bang_gia):
        """
        Lấy thông tin một bảng giá theo mã
        
        Args:
            ma_bang_gia (str): Mã bảng giá cần tìm
            
        Returns:
            BangGia: Đối tượng bảng giá hoặc None nếu không tìm thấy
        """
        for bg in self.get_all_bang_gia():
            if bg.ma_bang_gia == ma_bang_gia:
                return bg
        return None
    
    def get_bang_gia_hien_hanh(self):
        """
        Lấy bảng giá hiện hành (mới nhất)
        
        Returns:
            BangGia: Đối tượng bảng giá hiện hành hoặc None nếu không có
        """
        bang_gia_list = self.get_all_bang_gia()
        
        if not bang_gia_list:
            return None
        
        # Sắp xếp theo ngày áp dụng giảm dần (mới nhất đầu tiên)
        bang_gia_list.sort(key=lambda bg: bg.ngay_ap_dung, reverse=True)
        
        # Lấy bảng giá có ngày áp dụng gần nhất không vượt quá ngày hiện tại
        hien_hanh = None
        now = datetime.datetime.now()
        
        # Đặt trang_thai cho tất cả bảng giá là False
        for bg in bang_gia_list:
            bg.trang_thai = False
        
        for bg in bang_gia_list:
            if bg.ngay_ap_dung <= now:
                bg.trang_thai = True  # Đánh dấu bảng giá này là bảng giá hiện hành
                hien_hanh = bg
                break
        
        # Nếu không có bảng giá thỏa mãn, trả về bảng giá đầu tiên
        if hien_hanh is None and bang_gia_list:
            bang_gia_list[0].trang_thai = True
            hien_hanh = bang_gia_list[0]
        
        return hien_hanh
    
    def add_bang_gia(self, bang_gia):
        """
        Thêm bảng giá mới
        
        Args:
            bang_gia (BangGia): Đối tượng bảng giá cần thêm
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            bang_gia_list = self.get_all_bang_gia()
            
            # Kiểm tra mã bảng giá đã tồn tại chưa
            for bg in bang_gia_list:
                if bg.ma_bang_gia == bang_gia.ma_bang_gia:
                    return False
            
            bang_gia_list.append(bang_gia)
            
            with open(self.bang_gia_file, 'w', encoding='utf-8') as f:
                json.dump([bg.to_dict() for bg in bang_gia_list], f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Lỗi khi thêm bảng giá: {e}")
            return False
    
    # Phương thức tìm kiếm
    def search_khach_hang(self, keyword):
        """
        Tìm kiếm khách hàng theo từ khóa
        
        Args:
            keyword (str): Từ khóa tìm kiếm (tên, địa chỉ, số điện thoại,...)
            
        Returns:
            list: Danh sách khách hàng phù hợp
        """
        keyword = keyword.lower()
        result = []
        
        for kh in self.get_all_khach_hang():
            if (keyword in kh.ma_khach_hang.lower() or 
                keyword in kh.ho_ten.lower() or 
                keyword in kh.dia_chi.lower() or 
                keyword in kh.so_dien_thoai.lower() or 
                keyword in kh.ma_cong_to.lower()):
                result.append(kh)
        
        return result
    
    def search_hoa_don(self, keyword, thang=None, nam=None):
        """
        Tìm kiếm hóa đơn theo từ khóa và bộ lọc
        
        Args:
            keyword (str): Từ khóa tìm kiếm
            thang (int, optional): Tháng cần lọc
            nam (int, optional): Năm cần lọc
            
        Returns:
            list: Danh sách hóa đơn phù hợp
        """
        keyword = keyword.lower()
        result = []
        
        for hd in self.get_all_hoa_don():
            # Kiểm tra từ khóa
            ma_khach_hang = hd.ma_khach_hang.lower()
            ma_hoa_don = hd.ma_hoa_don.lower()
            
            khach_hang = self.get_khach_hang(hd.ma_khach_hang)
            ten_khach_hang = khach_hang.ho_ten.lower() if khach_hang else ""
            
            # Kiểm tra điều kiện lọc
            if keyword and not (keyword in ma_hoa_don or keyword in ma_khach_hang or keyword in ten_khach_hang):
                continue
                
            if thang is not None and hd.thang != thang:
                continue
                
            if nam is not None and hd.nam != nam:
                continue
                
            result.append(hd)
        
        return result
    
    def get_hoa_don_chua_thanh_toan(self):
        """
        Lấy danh sách hóa đơn chưa thanh toán
        
        Returns:
            list: Danh sách hóa đơn chưa thanh toán
        """
        return [hd for hd in self.get_all_hoa_don() if not hd.da_thanh_toan]
    
    def get_hoa_don_qua_han(self, so_ngay=30):
        """
        Lấy danh sách hóa đơn quá hạn thanh toán
        
        Args:
            so_ngay (int): Số ngày cho phép thanh toán sau khi tạo hóa đơn
            
        Returns:
            list: Danh sách hóa đơn quá hạn
        """
        now = datetime.datetime.now()
        han_thanh_toan = now - datetime.timedelta(days=so_ngay)
        
        result = []
        for hd in self.get_hoa_don_chua_thanh_toan():
            # Tạo ngày đầu tiên của tháng hóa đơn
            ngay_hoa_don = datetime.datetime(hd.nam, hd.thang, 1)
            
            # Kiểm tra nếu đã quá hạn
            if ngay_hoa_don < han_thanh_toan:
                # Tính số ngày quá hạn
                ngay_qua_han = (now - (ngay_hoa_don + datetime.timedelta(days=so_ngay))).days
                
                # Thêm thông tin số ngày quá hạn
                hd.ngay_qua_han = ngay_qua_han
                result.append(hd)
        
        return result
    
    def search_hoa_don_by_thang(self, thang):
        """
        Tìm kiếm hóa đơn theo tháng
        
        Args:
            thang (str): Tháng hóa đơn định dạng MM/YYYY
            
        Returns:
            list: Danh sách hóa đơn phù hợp
        """
        try:
            # Xử lý định dạng MM/YYYY
            if '/' in thang:
                parts = thang.split('/')
                if len(parts) == 2:
                    month = int(parts[0])
                    year = int(parts[1])
                    return [hd for hd in self.get_all_hoa_don() if hd.thang == month and hd.nam == year]
            
            # Nếu không đúng định dạng, trả về kết quả theo cách cũ
            return [hd for hd in self.get_all_hoa_don() if hd.thang == thang]
        except Exception:
            # Nếu có lỗi, trả về danh sách rỗng
            return []
    
    def get_hoa_don_by_khach_hang(self, ma_khach_hang):
        """
        Lấy danh sách hóa đơn của một khách hàng
        
        Args:
            ma_khach_hang (str): Mã khách hàng cần tìm
            
        Returns:
            list: Danh sách hóa đơn của khách hàng
        """
        return [hd for hd in self.get_all_hoa_don() if hd.ma_khach_hang == ma_khach_hang]
    
    def search_hoa_don_by_ma(self, ma_hoa_don):
        """
        Tìm kiếm hóa đơn theo mã
        
        Args:
            ma_hoa_don (str): Mã hóa đơn hoặc một phần mã hóa đơn
            
        Returns:
            list: Danh sách hóa đơn phù hợp
        """
        ma_hoa_don = ma_hoa_don.lower()
        return [hd for hd in self.get_all_hoa_don() if ma_hoa_don in hd.ma_hoa_don.lower()]
    
    # Phần 4: Thống kê và báo cáo
    def thong_ke_doanh_thu_theo_thang(self, thang=None, nam=None):
        """
        Thống kê doanh thu theo tháng
        
        Args:
            thang (int, optional): Tháng cần thống kê, mặc định là tháng hiện tại
            nam (int, optional): Năm cần thống kê, mặc định là năm hiện tại
            
        Returns:
            dict: Thông tin thống kê doanh thu
        """
        if thang is None:
            thang = datetime.datetime.now().month
        if nam is None:
            nam = datetime.datetime.now().year
            
        hoa_don_list = [hd for hd in self.get_all_hoa_don() if hd.thang == thang and hd.nam == nam]
        
        tong_doanh_thu = sum(hd.tong_tien for hd in hoa_don_list)
        so_hoa_don = len(hoa_don_list)
        da_thanh_toan = sum(1 for hd in hoa_don_list if hd.da_thanh_toan)
        chua_thanh_toan = so_hoa_don - da_thanh_toan
        tong_tien_da_thanh_toan = sum(hd.tong_tien for hd in hoa_don_list if hd.da_thanh_toan)
        tong_tien_chua_thanh_toan = tong_doanh_thu - tong_tien_da_thanh_toan
        
        return {
            "thang": thang,
            "nam": nam,
            "tong_doanh_thu": tong_doanh_thu,
            "so_hoa_don": so_hoa_don,
            "da_thanh_toan": da_thanh_toan,
            "chua_thanh_toan": chua_thanh_toan,
            "tong_tien_da_thanh_toan": tong_tien_da_thanh_toan,
            "tong_tien_chua_thanh_toan": tong_tien_chua_thanh_toan
        }
    
    def thong_ke_doanh_thu_theo_nam(self, nam=None):
        """
        Thống kê doanh thu theo năm
        
        Args:
            nam (int, optional): Năm cần thống kê, mặc định là năm hiện tại
            
        Returns:
            dict: Thông tin thống kê doanh thu theo năm và phân chia theo tháng
        """
        if nam is None:
            nam = datetime.datetime.now().year
            
        # Lấy tất cả hóa đơn trong năm
        hoa_don_list = [hd for hd in self.get_all_hoa_don() if hd.nam == nam]
        
        # Thống kê tổng năm
        tong_doanh_thu = sum(hd.tong_tien for hd in hoa_don_list)
        so_hoa_don = len(hoa_don_list)
        da_thanh_toan = sum(1 for hd in hoa_don_list if hd.da_thanh_toan)
        chua_thanh_toan = so_hoa_don - da_thanh_toan
        
        # Thống kê theo tháng
        thong_ke_thang = {}
        for thang in range(1, 13):
            hoa_don_thang = [hd for hd in hoa_don_list if hd.thang == thang]
            doanh_thu_thang = sum(hd.tong_tien for hd in hoa_don_thang)
            thong_ke_thang[thang] = {
                "doanh_thu": doanh_thu_thang,
                "so_hoa_don": len(hoa_don_thang),
                "da_thanh_toan": sum(1 for hd in hoa_don_thang if hd.da_thanh_toan),
                "chua_thanh_toan": sum(1 for hd in hoa_don_thang if not hd.da_thanh_toan)
            }
        
        return {
            "nam": nam,
            "tong_doanh_thu": tong_doanh_thu,
            "so_hoa_don": so_hoa_don,
            "da_thanh_toan": da_thanh_toan,
            "chua_thanh_toan": chua_thanh_toan,
            "theo_thang": thong_ke_thang
        }
    
    def thong_ke_tieu_thu_theo_thang(self, thang=None, nam=None):
        """
        Thống kê lượng điện tiêu thụ theo tháng
        
        Args:
            thang (int, optional): Tháng cần thống kê, mặc định là tháng hiện tại
            nam (int, optional): Năm cần thống kê, mặc định là năm hiện tại
            
        Returns:
            dict: Thông tin thống kê tiêu thụ điện
        """
        if thang is None:
            thang = datetime.datetime.now().month
        if nam is None:
            nam = datetime.datetime.now().year
            
        hoa_don_list = [hd for hd in self.get_all_hoa_don() if hd.thang == thang and hd.nam == nam]
        
        tong_tieu_thu = sum(hd.dien_tieu_thu for hd in hoa_don_list)
        so_khach_hang = len(set(hd.ma_khach_hang for hd in hoa_don_list))
        
        # Phân loại theo bậc tiêu thụ
        bac_1 = sum(1 for hd in hoa_don_list if hd.dien_tieu_thu <= 50)
        bac_2 = sum(1 for hd in hoa_don_list if 50 < hd.dien_tieu_thu <= 100)
        bac_3 = sum(1 for hd in hoa_don_list if 100 < hd.dien_tieu_thu <= 200)
        bac_4 = sum(1 for hd in hoa_don_list if 200 < hd.dien_tieu_thu <= 300)
        bac_5 = sum(1 for hd in hoa_don_list if 300 < hd.dien_tieu_thu <= 400)
        bac_6 = sum(1 for hd in hoa_don_list if hd.dien_tieu_thu > 400)
        
        return {
            "thang": thang,
            "nam": nam,
            "tong_tieu_thu": tong_tieu_thu,
            "so_khach_hang": so_khach_hang,
            "trung_binh_tieu_thu": tong_tieu_thu / so_khach_hang if so_khach_hang > 0 else 0,
            "phan_loai_tieu_thu": {
                "bac_1": bac_1,
                "bac_2": bac_2,
                "bac_3": bac_3,
                "bac_4": bac_4,
                "bac_5": bac_5,
                "bac_6": bac_6
            }
        }
    
    def thong_ke_tieu_thu_theo_nam(self, nam=None):
        """
        Thống kê lượng điện tiêu thụ theo năm
        
        Args:
            nam (int, optional): Năm cần thống kê, mặc định là năm hiện tại
            
        Returns:
            dict: Thông tin thống kê tiêu thụ điện theo năm và phân chia theo tháng
        """
        if nam is None:
            nam = datetime.datetime.now().year
            
        # Lấy tất cả hóa đơn trong năm
        hoa_don_list = [hd for hd in self.get_all_hoa_don() if hd.nam == nam]
        
        # Thống kê tổng năm
        tong_tieu_thu = sum(hd.dien_tieu_thu for hd in hoa_don_list)
        so_hoa_don = len(hoa_don_list)
        
        # Thống kê theo tháng
        thong_ke_thang = {}
        for thang in range(1, 13):
            hoa_don_thang = [hd for hd in hoa_don_list if hd.thang == thang]
            tieu_thu_thang = sum(hd.dien_tieu_thu for hd in hoa_don_thang)
            so_khach_hang = len(set(hd.ma_khach_hang for hd in hoa_don_thang))
            thong_ke_thang[thang] = {
                "tieu_thu": tieu_thu_thang,
                "so_khach_hang": so_khach_hang,
                "trung_binh_tieu_thu": tieu_thu_thang / so_khach_hang if so_khach_hang > 0 else 0
            }
        
        return {
            "nam": nam,
            "tong_tieu_thu": tong_tieu_thu,
            "so_hoa_don": so_hoa_don,
            "theo_thang": thong_ke_thang
        }
    
    def thong_ke_khach_hang(self):
        """
        Thống kê thông tin khách hàng
        
        Returns:
            dict: Thông tin thống kê khách hàng
        """
        khach_hang_list = self.get_all_khach_hang()
        so_khach_hang = len(khach_hang_list)
        
        # Thống kê theo địa chỉ
        dia_chi_dict = {}
        for kh in khach_hang_list:
            dia_chi = kh.dia_chi
            if dia_chi in dia_chi_dict:
                dia_chi_dict[dia_chi] += 1
            else:
                dia_chi_dict[dia_chi] = 1
        
        # Sắp xếp theo số lượng giảm dần
        dia_chi_thong_ke = sorted(
            [{"dia_chi": k, "so_luong": v} for k, v in dia_chi_dict.items()],
            key=lambda x: x["so_luong"],
            reverse=True
        )
        
        return {
            "tong_so_khach_hang": so_khach_hang,
            "theo_dia_chi": dia_chi_thong_ke
        }
    
    def thong_ke_no_dong(self, so_ngay=30):
        """
        Thống kê tình hình nợ đọng tiền điện
        
        Args:
            so_ngay (int): Số ngày cho phép thanh toán sau khi tạo hóa đơn
            
        Returns:
            dict: Thông tin thống kê nợ đọng
        """
        # Lấy danh sách hóa đơn quá hạn
        hoa_don_qua_han = self.get_hoa_don_qua_han(so_ngay)
        
        # Tổng tiền nợ
        tong_tien_no = sum(hd.tong_tien for hd in hoa_don_qua_han)
        
        # Thống kê theo thời gian nợ
        no_duoi_30_ngay = []
        no_30_60_ngay = []
        no_60_90_ngay = []
        no_tren_90_ngay = []
        
        for hd in hoa_don_qua_han:
            if hd.ngay_qua_han <= 30:
                no_duoi_30_ngay.append(hd)
            elif 30 < hd.ngay_qua_han <= 60:
                no_30_60_ngay.append(hd)
            elif 60 < hd.ngay_qua_han <= 90:
                no_60_90_ngay.append(hd)
            else:
                no_tren_90_ngay.append(hd)
        
        # Thống kê khách hàng nợ nhiều nhất
        khach_hang_no = {}
        for hd in hoa_don_qua_han:
            ma_khach_hang = hd.ma_khach_hang
            if ma_khach_hang in khach_hang_no:
                khach_hang_no[ma_khach_hang]["so_hoa_don"] += 1
                khach_hang_no[ma_khach_hang]["tong_tien"] += hd.tong_tien
            else:
                khach_hang = self.get_khach_hang(ma_khach_hang)
                khach_hang_no[ma_khach_hang] = {
                    "ma_khach_hang": ma_khach_hang,
                    "ten_khach_hang": khach_hang.ho_ten if khach_hang else "Không xác định",
                    "so_hoa_don": 1,
                    "tong_tien": hd.tong_tien
                }
        
        # Sắp xếp theo tổng tiền giảm dần
        top_khach_hang_no = sorted(
            list(khach_hang_no.values()),
            key=lambda x: x["tong_tien"],
            reverse=True
        )[:10]  # Lấy top 10
        
        return {
            "tong_hoa_don_no": len(hoa_don_qua_han),
            "tong_tien_no": tong_tien_no,
            "theo_thoi_gian": {
                "duoi_30_ngay": {
                    "so_hoa_don": len(no_duoi_30_ngay),
                    "tong_tien": sum(hd.tong_tien for hd in no_duoi_30_ngay)
                },
                "tu_30_60_ngay": {
                    "so_hoa_don": len(no_30_60_ngay),
                    "tong_tien": sum(hd.tong_tien for hd in no_30_60_ngay)
                },
                "tu_60_90_ngay": {
                    "so_hoa_don": len(no_60_90_ngay),
                    "tong_tien": sum(hd.tong_tien for hd in no_60_90_ngay)
                },
                "tren_90_ngay": {
                    "so_hoa_don": len(no_tren_90_ngay),
                    "tong_tien": sum(hd.tong_tien for hd in no_tren_90_ngay)
                }
            },
            "top_khach_hang_no": top_khach_hang_no
        }
    
    def xuat_bao_cao_json(self, bao_cao_data, file_path):
        """
        Xuất báo cáo ra file JSON
        
        Args:
            bao_cao_data (dict): Dữ liệu báo cáo
            file_path (str): Đường dẫn file JSON đầu ra
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(bao_cao_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Lỗi khi xuất báo cáo JSON: {e}")
            return False
    
    # Phương thức mới để làm tròn số tiền hóa đơn
    def lam_tron_so_tien_hoa_don(self):
        """
        Làm tròn số tiền của tất cả các hóa đơn thành số nguyên
        
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy tất cả hóa đơn
            hoa_don_list = self.get_all_hoa_don()
            
            # Làm tròn số tiền
            for hd in hoa_don_list:
                if hd.so_tien is not None:
                    hd.so_tien = round(hd.so_tien)
            
            # Lưu lại vào file
            with open(self.hoa_don_file, 'w', encoding='utf-8') as f:
                json.dump([hd.to_dict() for hd in hoa_don_list], f, ensure_ascii=False, indent=4)
            
            return True
        except Exception as e:
            print(f"Lỗi khi làm tròn số tiền hóa đơn: {e}")
            return False 