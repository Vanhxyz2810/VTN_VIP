#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
import time
from tabulate import tabulate
from models.khach_hang import KhachHang
from models.hoa_don import HoaDon
from models.bang_gia import BangGia
from utils.db_handler import DatabaseHandler
import sys
import random
import re
import shutil  # Thêm import cho shutil

# Thêm màu sắc cho ứng dụng
try:
    from colorama import init, Fore, Back, Style
    # Khởi tạo colorama
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    print("Đang cài đặt thư viện colorama...")
    os.system('pip install colorama')
    try:
        from colorama import init, Fore, Back, Style
        init(autoreset=True)
        HAS_COLORAMA = True
    except ImportError:
        HAS_COLORAMA = False
        print("Không thể cài đặt colorama. Giao diện sẽ không có màu sắc.")

# Thêm thư viện cho animation
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt
    HAS_RICH = True
    console = Console()
except ImportError:
    print("Đang cài đặt thư viện rich...")
    os.system('pip install rich')
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.prompt import Prompt
        HAS_RICH = True
        console = Console()
    except ImportError:
        HAS_RICH = False
        print("Không thể cài đặt rich. Giao diện sẽ không có animation đẹp.")

# Thêm thư mục gốc vào đường dẫn để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Màu sắc chủ đạo - tông màu vàng VTN
MAIN_COLOR = Fore.YELLOW if HAS_COLORAMA else ""
HIGHLIGHT_COLOR = Fore.WHITE + Back.YELLOW if HAS_COLORAMA else ""
TITLE_STYLE = Style.BRIGHT if HAS_COLORAMA else ""
RESET = Style.RESET_ALL if HAS_COLORAMA else ""

# Logo VTN
VTN_LOGO = f"""
{MAIN_COLOR}██╗   ██╗████████╗███╗   ██╗    ██╗   ██╗██╗██████╗ 
{MAIN_COLOR}██║   ██║╚══██╔══╝████╗  ██║    ██║   ██║██║██╔══██╗
{MAIN_COLOR}██║   ██║   ██║   ██╔██╗ ██║    ██║   ██║██║██████╔╝
{MAIN_COLOR}╚██╗ ██╔╝   ██║   ██║╚██╗██║    ╚██╗ ██╔╝██║██╔═══╝ 
{MAIN_COLOR} ╚████╔╝    ██║   ██║ ╚████║     ╚████╔╝ ██║██║     
{MAIN_COLOR}  ╚═══╝     ╚═╝   ╚═╝  ╚═══╝      ╚═══╝  ╚═╝╚═╝     
{MAIN_COLOR}        QUẢN LÝ ĐIỆN NĂNG CHUYÊN NGHIỆP{RESET}
"""

class QuanLyDien:
    def __init__(self):
        self.db = DatabaseHandler()
        self.current_menu = self.menu_chinh
        # Lấy kích thước terminal
        self.terminal_width = self._get_terminal_width()
        
    def _get_terminal_width(self):
        """Lấy độ rộng terminal để căn giữa nội dung"""
        try:
            # Sử dụng shutil để lấy kích thước terminal một cách đơn giản
            columns, _ = shutil.get_terminal_size()
            return columns
        except Exception:
            # Giá trị mặc định nếu không lấy được kích thước thực
            return 80
            
    def center_text(self, text, width=None):
        """Căn giữa text đơn giản, sử dụng khoảng cách"""
        if width is None:
            width = self._get_terminal_width()
            
        # Loại bỏ mã ANSI màu để tính độ dài thực
        text_no_color = self._strip_ansi_codes(text)
            
        # Tính số khoảng trắng cần thêm vào
        padding = (width - len(text_no_color)) // 2
        if padding <= 0:
            return text
            
        # Thêm khoảng trắng vào đầu chuỗi
        return ' ' * padding + text
    
    def _strip_ansi_codes(self, text):
        """Loại bỏ các mã ANSI trong chuỗi để tính toán độ dài thực"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def loading_animation(self, text="Đang tải"):
        """Hiển thị animation loading"""
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task(f"[yellow]{text}...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            chars = "|/-\\"
            for _ in range(10):
                for char in chars:
                    sys.stdout.write(f'\r{self.center_text(f"{text}... {char}", 50)}')
                    sys.stdout.flush()
                    time.sleep(0.1)
            print()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def simple_box(self, title, items):
        """Hiển thị menu đơn giản với tiêu đề và các mục, được căn giữa màn hình"""
        width = self._get_terminal_width()
        
        # Hiển thị tiêu đề
        title_line = f"{MAIN_COLOR}{TITLE_STYLE}{title}{RESET}"
        print(self.center_text(title_line))
        print()
        
        # Tính kích thước cần thiết cho menu 
        max_len = max(len(self._strip_ansi_codes(item)) for item in items)
        box_width = max_len + 10  # Thêm margin
        
        # Vẽ khung trên
        top_border = f"{MAIN_COLOR}┌{'─' * box_width}┐{RESET}"
        print(self.center_text(top_border))
        
        # Hiển thị các mục menu 
        for item in items:
            padding = box_width - len(self._strip_ansi_codes(item)) - 1
            item_text = f"{MAIN_COLOR}│ {item}{' ' * padding}│{RESET}"
            print(self.center_text(item_text))
        
        # Vẽ khung dưới
        bottom_border = f"{MAIN_COLOR}└{'─' * box_width}┘{RESET}"
        print(self.center_text(bottom_border))
        print()
    
    def menu_chinh(self):
        """Hiển thị menu chính của ứng dụng"""
        self.clear_screen()
        
        # Hiệu ứng đặc biệt cho logo VTN
        if HAS_RICH:
            from rich.align import Align
            from rich.text import Text
            from rich.console import Group
            from rich.panel import Panel
            from rich.prompt import Prompt
            
            # Hiệu ứng typing cho logo
            console.print()
            # Hiển thị logo với hiệu ứng xuất hiện từng dòng
            logo_lines = VTN_LOGO.strip().split('\n')
            for line in logo_lines:
                text = Text(line, style="yellow")
                console.print(Align.center(text))
                time.sleep(0.05)  # Hiệu ứng chậm hơn một chút để logo hiển thị từng dòng
            
            # Thêm dòng tiêu đề với hiệu ứng typing
            title_text = Text("PHẦN MỀM QUẢN LÝ TIỀN ĐIỆN CHUYÊN NGHIỆP", style="bold yellow")
            console.print()
            console.print(Align.center(title_text))
            
            # Hiệu ứng đường viền đặc biệt
            border_text = Text("═" * 60, style="yellow")
            console.print(Align.center(border_text))
            console.print()
            
            # Thêm thông tin thời gian hiện tại
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            time_text = Text(f"Thời gian hiện tại: {current_time}", style="cyan")
            console.print(Align.center(time_text))
            console.print()
            
            # Sử dụng rich để hiển thị menu chính với hiệu ứng xuất hiện
            menu_title = "[bold yellow]HỆ THỐNG QUẢN LÝ TIỀN ĐIỆN"
            menu_items = [
                "[bold yellow]1.[/bold yellow] [white]Quản lý khách hàng",
                "[bold yellow]2.[/bold yellow] [white]Quản lý hóa đơn",
                "[bold yellow]3.[/bold yellow] [white]Quản lý bảng giá điện",
                "[bold yellow]4.[/bold yellow] [white]Thống kê và báo cáo",
                "[bold yellow]0.[/bold yellow] [white]Thoát"
            ]
            
            # Hiển thị menu với hiệu ứng typing
            menu_panel = Panel(
                "\n".join(menu_items),
                title=menu_title,
                border_style="yellow",
                title_align="center",
                width=50
            )
            console.print(Align.center(menu_panel))
            
            # Hiển thị hướng dẫn
            console.print()
            console.print(Align.center(Text("Di chuyển bằng phím số và Enter để chọn", style="italic cyan")))
            console.print()
        else:
            # Hiển thị logo cho terminal thường với hiệu ứng typing đơn giản
            for line in VTN_LOGO.strip().split('\n'):
                print(self.center_text(line))
                time.sleep(0.05)
            
            print()
            
            # Hiển thị thời gian
            current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(self.center_text(f"{MAIN_COLOR}Thời gian hiện tại: {current_time}{RESET}"))
            print()
            
            # Sử dụng display_centered_menu để hiển thị menu căn giữa
            title = "HỆ THỐNG QUẢN LÝ TIỀN ĐIỆN"
            menu_items = [
                f"{MAIN_COLOR}1.{RESET} Quản lý khách hàng",
                f"{MAIN_COLOR}2.{RESET} Quản lý hóa đơn",
                f"{MAIN_COLOR}3.{RESET} Quản lý bảng giá điện",
                f"{MAIN_COLOR}4.{RESET} Thống kê và báo cáo",
                f"{MAIN_COLOR}0.{RESET} Thoát"
            ]
            
            self.display_centered_title(title, 60)
            self.display_centered_menu("MENU CHÍNH", menu_items)
            
            print(self.center_text(f"{MAIN_COLOR}Di chuyển bằng phím số và Enter để chọn{RESET}"))
            print()
        
        # Xử lý lựa chọn với hiệu ứng highlight
        if HAS_RICH:
            choice = Prompt.ask("[bold yellow]Nhập lựa chọn của bạn", console=console)
        else:
            choice = input(self.center_text("Nhập lựa chọn của bạn: "))
        
        try:
            if choice == "1":
                # Hiệu ứng chuyển trang
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold yellow]Đang chuyển đến Quản lý khách hàng..."),
                        transient=True,
                    ) as progress:
                        task = progress.add_task("[yellow]Đang tải...", total=100)
                        for i in range(101):
                            time.sleep(0.01)
                            progress.update(task, completed=i)
                else:
                    print(self.center_text(f"{MAIN_COLOR}Đang chuyển đến Quản lý khách hàng...{RESET}"))
                    time.sleep(0.7)
                
                self.current_menu = self.menu_khach_hang
                return True
            elif choice == "2":
                # Hiệu ứng chuyển trang
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold yellow]Đang chuyển đến Quản lý hóa đơn..."),
                        transient=True,
                    ) as progress:
                        task = progress.add_task("[yellow]Đang tải...", total=100)
                        for i in range(101):
                            time.sleep(0.01)
                            progress.update(task, completed=i)
                else:
                    print(self.center_text(f"{MAIN_COLOR}Đang chuyển đến Quản lý hóa đơn...{RESET}"))
                    time.sleep(0.7)
                
                self.current_menu = self.menu_hoa_don
                return True
            elif choice == "3":
                # Hiệu ứng chuyển trang
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold yellow]Đang chuyển đến Quản lý bảng giá điện..."),
                        transient=True,
                    ) as progress:
                        task = progress.add_task("[yellow]Đang tải...", total=100)
                        for i in range(101):
                            time.sleep(0.01)
                            progress.update(task, completed=i)
                else:
                    print(self.center_text(f"{MAIN_COLOR}Đang chuyển đến Quản lý bảng giá điện...{RESET}"))
                    time.sleep(0.7)
                
                self.current_menu = self.menu_bang_gia
                return True
            elif choice == "4":
                # Hiệu ứng chuyển trang
                if HAS_RICH:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[bold yellow]Đang chuyển đến Thống kê và báo cáo..."),
                        transient=True,
                    ) as progress:
                        task = progress.add_task("[yellow]Đang tải...", total=100)
                        for i in range(101):
                            time.sleep(0.01)
                            progress.update(task, completed=i)
                else:
                    print(self.center_text(f"{MAIN_COLOR}Đang chuyển đến Thống kê và báo cáo...{RESET}"))
                    time.sleep(0.7)
                
                self.current_menu = self.menu_thong_ke
                return True
            elif choice == "0":
                # Hiệu ứng thoát ứng dụng
                if HAS_RICH:
                    console.print()
                    console.print(Align.center(Text("Đang thoát ứng dụng...", style="bold red")))
                    
                    # Hiệu ứng đếm ngược
                    for i in range(3, 0, -1):
                        console.print(Align.center(Text(f"Thoát sau {i} giây...", style="red")))
                        time.sleep(0.7)
                else:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Đang thoát ứng dụng...{RESET}"))
                    # Hiệu ứng đếm ngược
                    for i in range(3, 0, -1):
                        print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Thoát sau {i} giây...{RESET}"), end="\r")
                        time.sleep(0.7)
                
                return False
            else:
                # Hiệu ứng thông báo lỗi
                if HAS_RICH:
                    console.print(Align.center(Panel(
                        "[bold red]Lựa chọn không hợp lệ!\nVui lòng nhập số từ 0-4.",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=50
                    )))
                else:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Lựa chọn không hợp lệ!{RESET}"))
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Vui lòng nhập số từ 0-4.{RESET}"))
                
                # Hiệu ứng đợi
                time.sleep(1.5)
                return True
        except KeyboardInterrupt:
            if HAS_RICH:
                console.print(Align.center(Text("\nĐang thoát chương trình...", style="bold red")))
            else:
                print(self.center_text(f"\n{Fore.RED if HAS_COLORAMA else ''}Đang thoát chương trình...{RESET}"))
            time.sleep(0.7)
            return False
    
    def menu_khach_hang(self):
        """Hiển thị menu quản lý khách hàng"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("QUẢN LÝ KHÁCH HÀNG", 60)
        
        if HAS_RICH:
            # Sử dụng rich để hiển thị menu
            menu_items = [
                "[bold yellow]1.[/bold yellow] [white]Xem danh sách khách hàng",
                "[bold yellow]2.[/bold yellow] [white]Thêm khách hàng mới",
                "[bold yellow]3.[/bold yellow] [white]Cập nhật thông tin khách hàng",
                "[bold yellow]4.[/bold yellow] [white]Xóa khách hàng",
                "[bold yellow]5.[/bold yellow] [white]Tìm kiếm khách hàng",
                "[bold yellow]0.[/bold yellow] [white]Quay lại menu chính"
            ]
            
            from rich.panel import Panel
            from rich.align import Align
            from rich.text import Text
            from rich.prompt import Prompt
            
            # Hiển thị panel căn giữa
            console.print(Align.center(
                Panel(
                    "\n".join(menu_items),
                    border_style="yellow",
                    title="[bold yellow]MENU KHÁCH HÀNG",
                    title_align="center"
                )
            ))
        else:
            # Sử dụng các hàm căn giữa đã cải tiến
            menu_items = [
                f"{MAIN_COLOR}1.{RESET} Xem danh sách khách hàng",
                f"{MAIN_COLOR}2.{RESET} Thêm khách hàng mới",
                f"{MAIN_COLOR}3.{RESET} Cập nhật thông tin khách hàng",
                f"{MAIN_COLOR}4.{RESET} Xóa khách hàng",
                f"{MAIN_COLOR}5.{RESET} Tìm kiếm khách hàng",
                f"{MAIN_COLOR}0.{RESET} Quay lại menu chính"
            ]
            
            self.display_centered_menu("MENU KHÁCH HÀNG", menu_items)
        
        # Xử lý lựa chọn
        choice = input(self.center_text("Nhập lựa chọn của bạn: "))
        try:
            if choice == "1":
                self.xem_khach_hang()
            elif choice == "2":
                self.them_khach_hang()
            elif choice == "3":
                self.cap_nhat_khach_hang()
            elif choice == "4":
                self.xoa_khach_hang()
            elif choice == "5":
                self.tim_kiem_khach_hang()
            elif choice == "0":
                self.current_menu = self.menu_chinh
            else:
                print(self.center_text(f"{Fore.RED}Lựa chọn không hợp lệ!{RESET}"))
                input(self.center_text("Nhấn Enter để tiếp tục..."))
            return True
        except KeyboardInterrupt:
            print(self.center_text("\nĐang thoát chương trình..."))
            return False
    
    def menu_hoa_don(self):
        """Hiển thị menu quản lý hóa đơn"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("QUẢN LÝ HÓA ĐƠN", 60)
        
        if HAS_RICH:
            # Sử dụng rich để hiển thị menu
            menu_items = [
                "[bold yellow]1.[/bold yellow] [white]Xem danh sách hóa đơn",
                "[bold yellow]2.[/bold yellow] [white]Tạo hóa đơn mới",
                "[bold yellow]3.[/bold yellow] [white]Cập nhật hóa đơn",
                "[bold yellow]4.[/bold yellow] [white]Xóa hóa đơn",
                "[bold yellow]5.[/bold yellow] [white]Tìm kiếm hóa đơn",
                "[bold yellow]6.[/bold yellow] [white]Xuất hóa đơn",
                "[bold yellow]0.[/bold yellow] [white]Quay lại menu chính"
            ]
            
            from rich.panel import Panel
            from rich.align import Align
            
            # Hiển thị panel căn giữa
            console.print(Align.center(
                Panel(
                    "\n".join(menu_items),
                    border_style="yellow",
                    title="[bold yellow]MENU HÓA ĐƠN",
                    title_align="center"
                )
            ))
        else:
            # Sử dụng các hàm căn giữa đã cải tiến
            menu_items = [
                f"{MAIN_COLOR}1.{RESET} Xem danh sách hóa đơn",
                f"{MAIN_COLOR}2.{RESET} Tạo hóa đơn mới",
                f"{MAIN_COLOR}3.{RESET} Cập nhật hóa đơn",
                f"{MAIN_COLOR}4.{RESET} Xóa hóa đơn",
                f"{MAIN_COLOR}5.{RESET} Tìm kiếm hóa đơn",
                f"{MAIN_COLOR}6.{RESET} Xuất hóa đơn",
                f"{MAIN_COLOR}0.{RESET} Quay lại menu chính"
            ]
            
            self.display_centered_menu("MENU HÓA ĐƠN", menu_items)
        
        # Xử lý lựa chọn
        choice = input(self.center_text("Nhập lựa chọn của bạn: "))
        try:
            if choice == "1":
                self.xem_hoa_don()
            elif choice == "2":
                self.tao_hoa_don()
            elif choice == "3":
                self.cap_nhat_hoa_don()
            elif choice == "4":
                self.xoa_hoa_don()
            elif choice == "5":
                self.tim_kiem_hoa_don()
            elif choice == "6":
                self.xuat_hoa_don()
            elif choice == "0":
                self.current_menu = self.menu_chinh
            else:
                print(self.center_text(f"{Fore.RED}Lựa chọn không hợp lệ!{RESET}"))
                input(self.center_text("Nhấn Enter để tiếp tục..."))
            return True
        except KeyboardInterrupt:
            print(self.center_text("\nĐang thoát chương trình..."))
            return False
    
    def menu_bang_gia(self):
        """Hiển thị menu quản lý bảng giá điện"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("QUẢN LÝ BẢNG GIÁ ĐIỆN", 60)
        
        if HAS_RICH:
            # Sử dụng rich để hiển thị menu
            menu_items = [
                "[bold yellow]1.[/bold yellow] [white]Xem bảng giá hiện tại",
                "[bold yellow]2.[/bold yellow] [white]Cập nhật bảng giá",
                "[bold yellow]3.[/bold yellow] [white]Xem lịch sử bảng giá",
                "[bold yellow]0.[/bold yellow] [white]Quay lại menu chính"
            ]
            
            from rich.panel import Panel
            from rich.align import Align
            
            # Hiển thị panel căn giữa
            console.print(Align.center(
                Panel(
                    "\n".join(menu_items),
                    border_style="yellow",
                    title="[bold yellow]MENU BẢNG GIÁ",
                    title_align="center"
                )
            ))
        else:
            # Sử dụng các hàm căn giữa đã cải tiến
            menu_items = [
                f"{MAIN_COLOR}1.{RESET} Xem bảng giá hiện tại",
                f"{MAIN_COLOR}2.{RESET} Cập nhật bảng giá",
                f"{MAIN_COLOR}3.{RESET} Xem lịch sử bảng giá",
                f"{MAIN_COLOR}0.{RESET} Quay lại menu chính"
            ]
            
            self.display_centered_menu("MENU BẢNG GIÁ", menu_items)
        
        # Xử lý lựa chọn
        choice = input(self.center_text("Nhập lựa chọn của bạn: "))
        try:
            if choice == "1":
                self.xem_bang_gia()
            elif choice == "2":
                self.cap_nhat_bang_gia()
            elif choice == "3":
                self.xem_lich_su_bang_gia()
            elif choice == "0":
                self.current_menu = self.menu_chinh
            else:
                print(self.center_text(f"{Fore.RED}Lựa chọn không hợp lệ!{RESET}"))
                input(self.center_text("Nhấn Enter để tiếp tục..."))
            return True
        except KeyboardInterrupt:
            print(self.center_text("\nĐang thoát chương trình..."))
            return False
    
    def menu_thong_ke(self):
        """Hiển thị menu thống kê và báo cáo"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("THỐNG KÊ VÀ BÁO CÁO", 60)
        
        if HAS_RICH:
            # Sử dụng rich để hiển thị menu
            menu_items = [
                "[bold yellow]1.[/bold yellow] [white]Thống kê tiêu thụ điện theo tháng",
                "[bold yellow]2.[/bold yellow] [white]Thống kê doanh thu theo tháng",
                "[bold yellow]3.[/bold yellow] [white]Báo cáo khách hàng tiêu thụ nhiều nhất",
                "[bold yellow]4.[/bold yellow] [white]Báo cáo hóa đơn chưa thanh toán",
                "[bold yellow]0.[/bold yellow] [white]Quay lại menu chính"
            ]
            
            from rich.panel import Panel
            from rich.align import Align
            
            # Hiển thị panel căn giữa
            console.print(Align.center(
                Panel(
                    "\n".join(menu_items),
                    border_style="yellow",
                    title="[bold yellow]MENU THỐNG KÊ",
                    title_align="center"
                )
            ))
        else:
            # Sử dụng các hàm căn giữa đã cải tiến
            menu_items = [
                f"{MAIN_COLOR}1.{RESET} Thống kê tiêu thụ điện theo tháng",
                f"{MAIN_COLOR}2.{RESET} Thống kê doanh thu theo tháng",
                f"{MAIN_COLOR}3.{RESET} Báo cáo khách hàng tiêu thụ nhiều nhất",
                f"{MAIN_COLOR}4.{RESET} Báo cáo hóa đơn chưa thanh toán",
                f"{MAIN_COLOR}0.{RESET} Quay lại menu chính"
            ]
            
            self.display_centered_menu("MENU THỐNG KÊ", menu_items)
        
        # Xử lý lựa chọn
        choice = input(self.center_text("Nhập lựa chọn của bạn: "))
        try:
            if choice == "1":
                self.thong_ke_tieu_thu()
            elif choice == "2":
                self.thong_ke_doanh_thu()
            elif choice == "3":
                self.bao_cao_khach_hang_tieu_thu_nhieu()
            elif choice == "4":
                self.bao_cao_hoa_don_chua_thanh_toan()
            elif choice == "0":
                self.current_menu = self.menu_chinh
            else:
                print(self.center_text(f"{Fore.RED}Lựa chọn không hợp lệ!{RESET}"))
                input(self.center_text("Nhấn Enter để tiếp tục..."))
            return True
        except KeyboardInterrupt:
            print(self.center_text("\nĐang thoát chương trình..."))
            return False
    
    # Các phương thức xử lý khách hàng
    def xem_khach_hang(self):
        """Hiển thị danh sách khách hàng"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("DANH SÁCH KHÁCH HÀNG", 60)
        
        # Lấy dữ liệu khách hàng
        khach_hang_list = self.db.get_all_khach_hang()
        
        # Hiệu ứng loading
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tải danh sách khách hàng..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tải danh sách khách hàng..."))
            time.sleep(0.5)
        
        if not khach_hang_list:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                from rich.text import Text
                
                console.print(Align.center(
                    Panel(
                        "[bold yellow]Chưa có khách hàng nào trong hệ thống!",
                        border_style="yellow",
                        title="[bold yellow]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.YELLOW if HAS_COLORAMA else ''}Chưa có khách hàng nào trong hệ thống!{RESET}"))
        else:
            # Chuẩn bị dữ liệu
            total_customers = len(khach_hang_list)
            
            if HAS_RICH:
                from rich.table import Table
                from rich.align import Align
                from rich.text import Text
                from rich.panel import Panel
                
                # Thông tin tổng quan
                summary_text = Text()
                summary_text.append("Tổng số khách hàng: ", style="bold green")
                summary_text.append(str(total_customers), style="white")
                console.print(Align.center(summary_text))
                console.print()
                
                # Tạo bảng
                table = Table(show_header=True, header_style="bold yellow", border_style="yellow")
                table.add_column("STT", style="dim", width=5, justify="center")
                table.add_column("Mã KH", style="cyan", width=15)
                table.add_column("Họ tên", style="white")
                table.add_column("Địa chỉ")
                table.add_column("Số điện thoại")
                table.add_column("Mã công tơ", style="green")
                
                # Bắt đầu hiển thị từng trang 10 khách hàng
                PAGE_SIZE = 10
                current_page = 1
                total_pages = (total_customers + PAGE_SIZE - 1) // PAGE_SIZE  # Làm tròn lên
                
                while True:
                    self.clear_screen()
                    self.display_centered_title("DANH SÁCH KHÁCH HÀNG", 60)
                    # Hiển thị tổng số khách hàng với Rich
                    summary_text = Text()
                    summary_text.append("Tổng số khách hàng: ", style="bold green")
                    summary_text.append(str(total_customers), style="white")
                    console.print(Align.center(summary_text))
                    console.print()
                    
                    # Tạo bảng mới cho mỗi trang
                    table = Table(show_header=True, header_style="bold yellow", border_style="yellow")
                    table.add_column("STT", style="dim", width=5, justify="center")
                    table.add_column("Mã KH", style="cyan", width=15)
                    table.add_column("Họ tên", style="white")
                    table.add_column("Địa chỉ")
                    table.add_column("Số điện thoại")
                    table.add_column("Mã công tơ", style="green")
                    
                    # Hiển thị khách hàng theo trang
                    start_idx = (current_page - 1) * PAGE_SIZE
                    end_idx = min(start_idx + PAGE_SIZE, total_customers)
                    
                    for i in range(start_idx, end_idx):
                        kh = khach_hang_list[i]
                        table.add_row(
                            str(i + 1),
                            kh.ma_khach_hang,
                            kh.ho_ten,
                            kh.dia_chi,
                            kh.so_dien_thoai,
                            kh.ma_cong_to
                        )
                    
                    console.print(Align.center(table))
                    
                    # Hiển thị thông tin phân trang
                    console.print(Align.center(
                        Text(f"Trang {current_page}/{total_pages}", style="yellow")
                    ))
                    
                    # Hiển thị menu điều hướng
                    nav_text = []
                    if current_page > 1:
                        nav_text.append("[P] Trang trước")
                    if current_page < total_pages:
                        nav_text.append("[N] Trang sau")
                    nav_text.append("[Q] Quay lại")
                    
                    console.print(Align.center(
                        Text(" | ".join(nav_text), style="bold yellow")
                    ))
                    
                    choice = Prompt.ask(
                        "[bold yellow]Nhập lựa chọn của bạn",
                        choices=["p", "n", "q", "P", "N", "Q"],
                        default="q",
                        console=console
                    ).lower()
                    
                    if choice == "p" and current_page > 1:
                        current_page -= 1
                    elif choice == "n" and current_page < total_pages:
                        current_page += 1
                    elif choice == "q":
                        break
            else:
                # Hiển thị bảng với tabulate cho terminal thường
                headers = ["STT", "Mã KH", "Họ tên", "Địa chỉ", "Số điện thoại", "Mã công tơ"]
                
                # Thêm màu cho header nếu có colorama
                if HAS_COLORAMA:
                    headers = [f"{MAIN_COLOR}{header}{RESET}" for header in headers]
                
                print(self.center_text(f"Tổng số khách hàng: {total_customers}"))
                print()
                
                # Hiển thị từng trang 10 khách hàng
                PAGE_SIZE = 10
                current_page = 1
                total_pages = (total_customers + PAGE_SIZE - 1) // PAGE_SIZE  # Làm tròn lên
                
                while True:
                    self.clear_screen()
                    self.display_centered_title("DANH SÁCH KHÁCH HÀNG", 60)
                    print(self.center_text(f"Tổng số khách hàng: {total_customers}"))
                    print()
                    
                    # Hiển thị khách hàng theo trang
                    start_idx = (current_page - 1) * PAGE_SIZE
                    end_idx = min(start_idx + PAGE_SIZE, total_customers)
                    
                    data = []
                    for i in range(start_idx, end_idx):
                        kh = khach_hang_list[i]
                        data.append([
                            i + 1,
                            kh.ma_khach_hang,
                            kh.ho_ten, 
                            kh.dia_chi, 
                            kh.so_dien_thoai, 
                            kh.ma_cong_to
                        ])
                    
                    # Hiển thị bảng căn giữa
                    table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
                    for line in table.split('\n'):
                        print(self.center_text(line))
                    
                    # Hiển thị thông tin phân trang
                    print(self.center_text(f"Trang {current_page}/{total_pages}"))
                    print()
                    
                    # Hiển thị menu điều hướng
                    nav_options = []
                    if current_page > 1:
                        nav_options.append("P - Trang trước")
                    if current_page < total_pages:
                        nav_options.append("N - Trang sau")
                    nav_options.append("Q - Quay lại")
                    
                    print(self.center_text(" | ".join(nav_options)))
                    
                    choice = input(self.center_text("Nhập lựa chọn của bạn: ")).lower()
                    
                    if choice == "p" and current_page > 1:
                        current_page -= 1
                    elif choice == "n" and current_page < total_pages:
                        current_page += 1
                    elif choice == "q":
                        break
    
    def them_khach_hang(self):
        self.clear_screen()
        self.display_centered_title("THÊM KHÁCH HÀNG MỚI", 50)
        print(self.center_text("-" * 50))
        
        # Hiệu ứng nhập thông tin với typing effect
        if HAS_RICH:
            from rich.prompt import Prompt
            from rich.style import Style
            
            ho_ten = Prompt.ask(
                "[bold yellow]Họ tên", 
                console=console
            )
            dia_chi = Prompt.ask(
                "[bold yellow]Địa chỉ", 
                console=console
            )
            so_dien_thoai = Prompt.ask(
                "[bold yellow]Số điện thoại", 
                console=console
            )
            ma_cong_to = Prompt.ask(
                "[bold yellow]Mã công tơ", 
                console=console
            )
        else:
            # Hiệu ứng typing cho terminal thường
            print(self.center_text("Vui lòng nhập thông tin khách hàng:"))
            print()
            
            def typing_effect(text):
                centered_text = self.center_text(text)
                for char in centered_text:
                    print(char, end='', flush=True)
                    time.sleep(0.01)
                print()
            
            typing_effect("Họ tên: ")
            ho_ten = input()
            typing_effect("Địa chỉ: ")
            dia_chi = input()
            typing_effect("Số điện thoại: ")
            so_dien_thoai = input()
            typing_effect("Mã công tơ: ")
            ma_cong_to = input()
        
        # Tạo mã khách hàng tự động
        ma_khach_hang = f"KH{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Hiệu ứng loading khi đang thêm khách hàng
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang thêm khách hàng..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            # Hiệu ứng loading đơn giản
            print()
            loading_chars = "|/-\\"
            for _ in range(15):
                for char in loading_chars:
                    sys.stdout.write(f'\r{self.center_text(f"Đang thêm khách hàng... {char}", 50)}')
                    sys.stdout.flush()
                    time.sleep(0.1)
            print()
        
        # Thêm khách hàng vào DB
        khach_hang = KhachHang(ma_khach_hang, ho_ten, dia_chi, so_dien_thoai, ma_cong_to)
        success = self.db.add_khach_hang(khach_hang)
        
        # Hiệu ứng thông báo thành công
        if success:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                from rich.text import Text
                
                success_text = Text()
                success_text.append("\n✓ ", style="bold green")
                success_text.append("Đã thêm khách hàng thành công!\n\n", style="bold white")
                success_text.append("Mã khách hàng: ", style="yellow")
                success_text.append(ma_khach_hang, style="bold white")
                success_text.append("\nHọ tên: ", style="yellow")
                success_text.append(ho_ten, style="white")
                success_text.append("\n")
                
                console.print(Align.center(
                    Panel(
                        success_text,
                        title="[bold green]THÀNH CÔNG",
                        border_style="green",
                        width=60,
                        padding=(1, 2)
                    )
                ))
            else:
                # Animation thành công đơn giản
                print("\n")
                success_msg = f"Đã thêm khách hàng thành công với mã: {ma_khach_hang}"
                
                # Hiệu ứng flash
                for _ in range(3):
                    print(self.center_text(f"{MAIN_COLOR}{success_msg}{RESET}"))
                    time.sleep(0.3)
                    sys.stdout.write("\033[F\033[K")  # Xóa dòng trước đó
                    time.sleep(0.2)
                    
                print(self.center_text(f"{MAIN_COLOR}{success_msg}{RESET}"))
                print(self.center_text(f"Họ tên: {ho_ten}"))
        else:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold red]Thêm khách hàng thất bại!",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=50
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Thêm khách hàng thất bại!{RESET}"))
        
        # Hiệu ứng nhấn enter để tiếp tục
        if HAS_RICH:
            from rich.text import Text
            from rich.align import Align
            console.print("\n")
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
            input()
        else:
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def cap_nhat_khach_hang(self):
        self.clear_screen()
        self.display_centered_title("CẬP NHẬT THÔNG TIN KHÁCH HÀNG", 50)
        print(self.center_text("-" * 50))
        
        # Yêu cầu người dùng nhập mã khách hàng
        if HAS_RICH:
            from rich.prompt import Prompt
            from rich.align import Align
            from rich.panel import Panel
            from rich.text import Text
            from rich.table import Table
            
            ma_khach_hang = Prompt.ask(
                "[bold yellow]Nhập mã khách hàng cần cập nhật",
                console=console
            )
        else:
            ma_khach_hang = input(self.center_text("Nhập mã khách hàng cần cập nhật: "))
        
        # Hiệu ứng tìm kiếm
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm khách hàng..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tìm kiếm..."))
            time.sleep(0.8)
        
        # Tìm khách hàng theo mã
        khach_hang = self.db.get_khach_hang(ma_khach_hang)
        
        if not khach_hang:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        f"[bold red]Không tìm thấy khách hàng với mã [white]{ma_khach_hang}[/white]!",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"\nKhông tìm thấy khách hàng với mã {ma_khach_hang}!"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Hiển thị thông tin hiện tại
        if HAS_RICH:
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Thuộc tính", style="yellow")
            info_table.add_column("Giá trị", style="white")
            
            info_table.add_row("Mã khách hàng", khach_hang.ma_khach_hang)
            info_table.add_row("Họ tên", khach_hang.ho_ten)
            info_table.add_row("Địa chỉ", khach_hang.dia_chi)
            info_table.add_row("Số điện thoại", khach_hang.so_dien_thoai)
            info_table.add_row("Mã công tơ", khach_hang.ma_cong_to)
            
            console.print(Align.center(
                Panel(
                    info_table,
                    title="[bold yellow]THÔNG TIN HIỆN TẠI",
                    border_style="yellow",
                    width=60
                )
            ))
            
            console.print()
            console.print(Align.center(Text("Nhập thông tin mới (để trống nếu không thay đổi)", style="bold yellow")))
            
            ho_ten = Prompt.ask(
                f"[yellow]Họ tên[/yellow] [[{khach_hang.ho_ten}]]", 
                default=khach_hang.ho_ten,
                console=console
            )
            dia_chi = Prompt.ask(
                f"[yellow]Địa chỉ[/yellow] [[{khach_hang.dia_chi}]]", 
                default=khach_hang.dia_chi,
                console=console
            )
            so_dien_thoai = Prompt.ask(
                f"[yellow]Số điện thoại[/yellow] [[{khach_hang.so_dien_thoai}]]", 
                default=khach_hang.so_dien_thoai,
                console=console
            )
            ma_cong_to = Prompt.ask(
                f"[yellow]Mã công tơ[/yellow] [[{khach_hang.ma_cong_to}]]", 
                default=khach_hang.ma_cong_to,
                console=console
            )
        else:
            print(self.center_text(f"\nThông tin hiện tại của khách hàng {khach_hang.ho_ten}:"))
            print(self.center_text(f"Mã khách hàng: {khach_hang.ma_khach_hang}"))
            print(self.center_text(f"Họ tên: {khach_hang.ho_ten}"))
            print(self.center_text(f"Địa chỉ: {khach_hang.dia_chi}"))
            print(self.center_text(f"Số điện thoại: {khach_hang.so_dien_thoai}"))
            print(self.center_text(f"Mã công tơ: {khach_hang.ma_cong_to}"))
            
            print(self.center_text("\nNhập thông tin mới (để trống nếu không thay đổi):"))
            ho_ten = input(self.center_text(f"Họ tên [{khach_hang.ho_ten}]: "))
            dia_chi = input(self.center_text(f"Địa chỉ [{khach_hang.dia_chi}]: "))
            so_dien_thoai = input(self.center_text(f"Số điện thoại [{khach_hang.so_dien_thoai}]: "))
            ma_cong_to = input(self.center_text(f"Mã công tơ [{khach_hang.ma_cong_to}]: "))
        
        # Cập nhật thông tin
        new_ho_ten = ho_ten if ho_ten else khach_hang.ho_ten
        new_dia_chi = dia_chi if dia_chi else khach_hang.dia_chi
        new_so_dien_thoai = so_dien_thoai if so_dien_thoai else khach_hang.so_dien_thoai
        new_ma_cong_to = ma_cong_to if ma_cong_to else khach_hang.ma_cong_to
        
        # Tạo đối tượng khách hàng mới với thông tin đã cập nhật
        updated_khach_hang = KhachHang(
            khach_hang.ma_khach_hang,
            new_ho_ten,
            new_dia_chi,
            new_so_dien_thoai,
            new_ma_cong_to
        )
        
        # Hiệu ứng đang cập nhật
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang cập nhật thông tin..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print()
            print(self.center_text("Đang cập nhật thông tin..."))
            time.sleep(0.8)
        
        # Cập nhật vào cơ sở dữ liệu
        success = self.db.update_khach_hang(updated_khach_hang)
        
        if success:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        f"[bold green]Đã cập nhật thông tin khách hàng [white]{khach_hang.ma_khach_hang}[/white] thành công!",
                        border_style="green",
                        title="[bold green]THÀNH CÔNG",
                        width=60
                    )
                ))
                
                # Hiển thị so sánh thông tin trước và sau
                compare_table = Table(title="So sánh thông tin", show_header=True, header_style="bold yellow", border_style="yellow")
                compare_table.add_column("Thuộc tính", style="yellow")
                compare_table.add_column("Thông tin cũ", style="dim")
                compare_table.add_column("Thông tin mới", style="green")
                
                compare_table.add_row("Họ tên", khach_hang.ho_ten, new_ho_ten)
                compare_table.add_row("Địa chỉ", khach_hang.dia_chi, new_dia_chi)
                compare_table.add_row("Số điện thoại", khach_hang.so_dien_thoai, new_so_dien_thoai)
                compare_table.add_row("Mã công tơ", khach_hang.ma_cong_to, new_ma_cong_to)
                
                console.print(Align.center(compare_table))
            else:
                print(self.center_text(f"\n{Fore.GREEN if HAS_COLORAMA else ''}Đã cập nhật thông tin khách hàng {khach_hang.ma_khach_hang} thành công!{RESET}"))
                
                # Hiển thị thông tin đã cập nhật
                print(self.center_text("\nThông tin sau khi cập nhật:"))
                print(self.center_text(f"Họ tên: {new_ho_ten}"))
                print(self.center_text(f"Địa chỉ: {new_dia_chi}"))
                print(self.center_text(f"Số điện thoại: {new_so_dien_thoai}"))
                print(self.center_text(f"Mã công tơ: {new_ma_cong_to}"))
        else:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold red]Cập nhật thông tin khách hàng thất bại!",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"\n{Fore.RED if HAS_COLORAMA else ''}Cập nhật thông tin khách hàng thất bại!{RESET}"))
        
        # Nhấn Enter để tiếp tục
        if HAS_RICH:
            from rich.text import Text
            from rich.align import Align
            console.print("\n")
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
            input()
        else:
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def xoa_khach_hang(self):
        self.clear_screen()
        self.display_centered_title("XÓA KHÁCH HÀNG", 50)
        print(self.center_text("-" * 50))
        
        # Yêu cầu người dùng nhập mã khách hàng
        if HAS_RICH:
            from rich.prompt import Prompt
            ma_khach_hang = Prompt.ask("[bold yellow]Nhập mã khách hàng cần xóa", console=console)
        else:
            ma_khach_hang = input(self.center_text("Nhập mã khách hàng cần xóa: "))
        
        # Hiệu ứng tìm kiếm
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm khách hàng..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tìm kiếm..."))
            time.sleep(1)
        
        # Tìm khách hàng theo mã
        khach_hang = self.db.get_khach_hang(ma_khach_hang)
        
        if not khach_hang:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                console.print(Align.center(
                    Panel(
                        f"[bold red]Không tìm thấy khách hàng với mã {ma_khach_hang}!",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"\nKhông tìm thấy khách hàng với mã {ma_khach_hang}!"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Hiển thị thông tin khách hàng với animation
        if HAS_RICH:
            from rich.panel import Panel
            from rich.table import Table
            from rich.align import Align
            
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Thuộc tính", style="yellow")
            info_table.add_column("Giá trị", style="white")
            
            info_table.add_row("Mã khách hàng", khach_hang.ma_khach_hang)
            info_table.add_row("Họ tên", khach_hang.ho_ten)
            info_table.add_row("Địa chỉ", khach_hang.dia_chi)
            info_table.add_row("Số điện thoại", khach_hang.so_dien_thoai)
            info_table.add_row("Mã công tơ", khach_hang.ma_cong_to)
            
            console.print(Align.center(
                Panel(
                    info_table,
                    title="[bold yellow]THÔNG TIN KHÁCH HÀNG CẦN XÓA",
                    border_style="yellow",
                    width=60
                )
            ))
        else:
            print(self.center_text(f"\nThông tin khách hàng cần xóa:"))
            print(self.center_text(f"Mã khách hàng: {khach_hang.ma_khach_hang}"))
            print(self.center_text(f"Họ tên: {khach_hang.ho_ten}"))
            print(self.center_text(f"Địa chỉ: {khach_hang.dia_chi}"))
            print(self.center_text(f"Số điện thoại: {khach_hang.so_dien_thoai}"))
            print(self.center_text(f"Mã công tơ: {khach_hang.ma_cong_to}"))
        
        # Xác nhận xóa với hiệu ứng đặc biệt
        if HAS_RICH:
            from rich.prompt import Confirm
            confirm = Confirm.ask(
                "\n[bold red]Bạn có chắc muốn xóa khách hàng này?[/bold red]",
                console=console
            )
        else:
            # Hiệu ứng cảnh báo cho terminal thường
            warning = "CẢNH BÁO: Dữ liệu sẽ bị xóa vĩnh viễn và không thể khôi phục!"
            
            # Hiệu ứng nhấp nháy cho cảnh báo
            for _ in range(3):
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}{warning}{RESET}"))
                time.sleep(0.5)
                sys.stdout.write("\033[F\033[K")  # Xóa dòng trước đó
                time.sleep(0.2)
                
            print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}{warning}{RESET}"))
            confirm = input(self.center_text("\nBạn có chắc muốn xóa khách hàng này? (y/n): "))
            confirm = confirm.lower() == 'y'
        
        if confirm:
            # Hiệu ứng loading khi đang xóa
            if HAS_RICH:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold red]Đang xóa khách hàng..."),
                    transient=True,
                ) as progress:
                    task = progress.add_task("[red]Đang xử lý...", total=100)
                    for i in range(101):
                        time.sleep(0.02)
                        progress.update(task, completed=i)
            else:
                # Hiệu ứng loading đơn giản
                print()
                loading_chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
                for _ in range(15):
                    for char in loading_chars:
                        sys.stdout.write(f'\r{self.center_text(f"Đang xóa khách hàng... {char}", 50)}')
                        sys.stdout.flush()
                        time.sleep(0.1)
                print()
            
            # Xóa khách hàng
            success = self.db.delete_khach_hang(ma_khach_hang)
            
            if success:
                if HAS_RICH:
                    from rich.panel import Panel
                    from rich.align import Align
                    console.print("\n")
                    console.print(Align.center(
                        Panel(
                            f"[bold green]Đã xóa khách hàng [white]{khach_hang.ho_ten}[/white] thành công!",
                            border_style="green",
                            title="[bold green]THÀNH CÔNG",
                            width=60
                        )
                    ))
                else:
                    print(self.center_text(f"\n{Fore.GREEN if HAS_COLORAMA else ''}Đã xóa khách hàng {khach_hang.ho_ten} thành công!{RESET}"))
            else:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Xóa khách hàng thất bại!",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=50
                        )
                    ))
                else:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Xóa khách hàng thất bại!{RESET}"))
        else:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold yellow]Đã hủy xóa khách hàng.",
                        border_style="yellow",
                        title="[bold yellow]THÔNG BÁO",
                        width=50
                    )
                ))
            else:
                print(self.center_text("\nĐã hủy xóa khách hàng."))
        
        # Hiệu ứng nhấn Enter
        if HAS_RICH:
            from rich.text import Text
            from rich.align import Align
            console.print("\n")
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
            input()
        else:
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def tim_kiem_khach_hang(self):
        self.clear_screen()
        self.display_centered_title("TÌM KIẾM KHÁCH HÀNG", 50)
        print(self.center_text("-" * 50))
        
        # Yêu cầu người dùng nhập từ khóa tìm kiếm
        if HAS_RICH:
            from rich.prompt import Prompt
            keyword = Prompt.ask(
                "[bold yellow]Nhập từ khóa tìm kiếm[/bold yellow] [white](tên, địa chỉ, số điện thoại, mã công tơ)",
                console=console
            )
        else:
            keyword = input(self.center_text("Nhập từ khóa tìm kiếm (tên, địa chỉ, số điện thoại, mã công tơ): "))
        
        # Hiệu ứng đang tìm kiếm
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold yellow]Đang tìm kiếm '{keyword}'..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print()
            print(self.center_text(f"Đang tìm kiếm '{keyword}'..."))
            
            # Hiệu ứng loading đơn giản
            loading_chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
            for _ in range(10):
                for char in loading_chars:
                    sys.stdout.write(f'\r{self.center_text(f"Đang tìm kiếm... {char}", 50)}')
                    sys.stdout.flush()
                    time.sleep(0.05)
            print("\n")
        
        # Tìm kiếm khách hàng
        khach_hang_list = self.db.search_khach_hang(keyword)
        
        # Hiển thị kết quả
        if not khach_hang_list:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                console.print(Align.center(
                    Panel(
                        f"[bold red]Không tìm thấy khách hàng phù hợp với từ khóa '[white]{keyword}[/white]'!",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"\n{Fore.RED if HAS_COLORAMA else ''}Không tìm thấy khách hàng phù hợp với từ khóa '{keyword}'!{RESET}"))
        else:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                from rich.table import Table
                
                # Hiển thị số lượng kết quả tìm thấy
                console.print(Align.center(
                    Panel(
                        f"[bold green]Đã tìm thấy [white]{len(khach_hang_list)}[/white] khách hàng phù hợp với từ khóa '[white]{keyword}[/white]'",
                        border_style="green",
                        title="[bold green]KẾT QUẢ TÌM KIẾM",
                        width=70
                    )
                ))
                
                # Tạo bảng hiển thị kết quả
                table = Table(show_header=True, header_style="bold yellow", border_style="yellow")
                table.add_column("Mã KH", style="dim")
                table.add_column("Họ tên", style="white")
                table.add_column("Địa chỉ")
                table.add_column("Số điện thoại")
                table.add_column("Mã công tơ")
                
                # Thêm dữ liệu vào bảng
                for kh in khach_hang_list:
                    # Highlight phần khớp với từ khóa
                    ho_ten = kh.ho_ten
                    dia_chi = kh.dia_chi
                    so_dien_thoai = kh.so_dien_thoai
                    
                    if keyword.lower() in ho_ten.lower():
                        ho_ten = ho_ten.replace(keyword, f"[bold yellow]{keyword}[/bold yellow]")
                    if keyword.lower() in dia_chi.lower():
                        dia_chi = dia_chi.replace(keyword, f"[bold yellow]{keyword}[/bold yellow]")
                    if keyword.lower() in so_dien_thoai.lower():
                        so_dien_thoai = so_dien_thoai.replace(keyword, f"[bold yellow]{keyword}[/bold yellow]")
                    
                    table.add_row(
                        kh.ma_khach_hang,
                        ho_ten,
                        dia_chi,
                        so_dien_thoai,
                        kh.ma_cong_to
                    )
                
                console.print(Align.center(table))
            else:
                print(self.center_text(f"\n{MAIN_COLOR}Đã tìm thấy {len(khach_hang_list)} khách hàng:{RESET}"))
                headers = ["Mã KH", "Họ tên", "Địa chỉ", "Số điện thoại", "Mã công tơ"]
                
                # Thêm màu cho header nếu có colorama
                if HAS_COLORAMA:
                    headers = [f"{MAIN_COLOR}{header}{RESET}" for header in headers]
                
                data = [[kh.ma_khach_hang, kh.ho_ten, kh.dia_chi, kh.so_dien_thoai, kh.ma_cong_to] 
                       for kh in khach_hang_list]
                
                # Hiển thị bảng căn giữa
                table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
                for line in table.split('\n'):
                    print(self.center_text(line))
        
        # Hiệu ứng nhấn Enter
        if HAS_RICH:
            from rich.text import Text
            from rich.align import Align
            console.print("\n")
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
            input()
        else:
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    # Các phương thức xử lý hóa đơn
    def xem_hoa_don(self):
        """Hiển thị danh sách hóa đơn"""
        self.clear_screen()
        
        # Hiển thị logo VTN căn giữa màn hình
        for line in VTN_LOGO.strip().split('\n'):
            print(self.center_text(line))
        print()
        
        if HAS_RICH:
            console.print(Panel.fit(
                "[bold yellow]DANH SÁCH HÓA ĐƠN",
                border_style="yellow"
            ))
        else:
            self.display_centered_title("DANH SÁCH HÓA ĐƠN", 50)

        hoa_don_list = self.db.get_all_hoa_don()
        
        if not hoa_don_list:
            if HAS_RICH:
                console.print("[bold red]Chưa có hóa đơn nào trong hệ thống![/bold red]")
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Chưa có hóa đơn nào trong hệ thống!{RESET}", 80))
        else:
            headers = ["Mã HĐ", "Mã KH", "Thời gian", "Chỉ số cũ", "Chỉ số mới", "Tiêu thụ", "Thành tiền", "Đã thanh toán"]
            data = []
            
            for hd in hoa_don_list:
                # Lấy thông tin khách hàng
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                khach_hang_name = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
                
                # Định dạng thời gian từ thang và nam
                thoi_gian_str = f"{hd.thang}/{hd.nam}"
                
                # Định dạng trạng thái thanh toán
                trang_thai = "Đã thanh toán" if hd.da_thanh_toan else "Chưa thanh toán"
                
                # Định dạng tiền
                thanh_tien_str = f"{hd.so_tien:,}đ".replace(",", ".")
                
                row = [
                    hd.ma_hoa_don,
                    f"{hd.ma_khach_hang} ({khach_hang_name})",
                    thoi_gian_str,
                    f"{hd.chi_so_dau:,}",
                    f"{hd.chi_so_cuoi:,}",
                    f"{hd.chi_so_cuoi - hd.chi_so_dau:,}",
                    thanh_tien_str,
                    trang_thai
                ]
                data.append(row)
            
            # Sử dụng màu vàng cho header nếu có colorama
            if HAS_COLORAMA and not HAS_RICH:
                headers = [f"{MAIN_COLOR}{header}{RESET}" for header in headers]
                
            # Thêm màu cho trạng thái thanh toán
            if HAS_COLORAMA and not HAS_RICH:
                for i, row in enumerate(data):
                    if "Đã thanh toán" in row[-1]:
                        data[i][-1] = f"{Fore.GREEN}✅ Đã thanh toán{RESET}"
                    else:
                        data[i][-1] = f"{Fore.RED}❌ Chưa thanh toán{RESET}"
            
            # Hiển thị bảng với rich nếu có, nếu không thì dùng tabulate thông thường
            if HAS_RICH:
                from rich.table import Table
                table = Table(show_header=True, header_style="bold yellow", border_style="yellow")
                # Thêm các cột với justify="center" để căn giữa
                for header in headers:
                    table.add_column(header)
                for row in data:
                    styled_row = []
                    for i, cell in enumerate(row):
                        if i == 7:  # Cột trạng thái
                            if "Đã thanh toán" in cell:
                                styled_row.append("[green]✅ Đã thanh toán[/green]")
                            else:
                                styled_row.append("[red]❌ Chưa thanh toán[/red]")
                        else:
                            styled_row.append(str(cell))
                    table.add_row(*styled_row)
                console.print(table)
            else:
                # Tạo và hiển thị bảng căn giữa màn hình
                table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
                for line in table.split('\n'):
                    print(self.center_text(line))
        
        input(self.center_text("Nhấn Enter để tiếp tục..."))
    
    def tao_hoa_don(self):
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("TẠO HÓA ĐƠN MỚI", 50)
        
        # Hiển thị danh sách khách hàng để chọn
        khach_hang_list = self.db.get_all_khach_hang()
        
        if not khach_hang_list:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                console.print(Align.center(
                    Panel(
                        "[bold red]Chưa có khách hàng nào trong hệ thống! Vui lòng thêm khách hàng trước.",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text("Chưa có khách hàng nào trong hệ thống! Vui lòng thêm khách hàng trước."))
            
            # Hiệu ứng nhấn Enter
            if HAS_RICH:
                from rich.text import Text
                from rich.align import Align
                console.print("\n")
                console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
                input()
            else:
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Hiển thị danh sách khách hàng
        if HAS_RICH:
            from rich.table import Table
            from rich.align import Align
            
            # Tạo bảng hiển thị danh sách khách hàng
            table = Table(title="DANH SÁCH KHÁCH HÀNG", 
                         show_header=True, 
                         header_style="bold yellow", 
                         border_style="yellow",
                         title_style="bold yellow")
            
            table.add_column("STT", style="dim", justify="center")
            table.add_column("Mã KH", style="cyan", justify="center")
            table.add_column("Họ tên")
            table.add_column("Địa chỉ")
            table.add_column("Mã công tơ", justify="center")
            
            for i, kh in enumerate(khach_hang_list):
                table.add_row(
                    str(i+1),
                    kh.ma_khach_hang,
                    kh.ho_ten,
                    kh.dia_chi,
                    kh.ma_cong_to
                )
            
            console.print(Align.center(table))
        else:
            print(self.center_text("DANH SÁCH KHÁCH HÀNG:"))
            headers = ["STT", "Mã KH", "Họ tên", "Địa chỉ", "Mã công tơ"]
            data = [[i+1, kh.ma_khach_hang, kh.ho_ten, kh.dia_chi, kh.ma_cong_to] 
                  for i, kh in enumerate(khach_hang_list)]
            
            # Hiển thị bảng căn giữa
            table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
            for line in table.split('\n'):
                print(self.center_text(line))
        
        # Chọn khách hàng
        try:
            if HAS_RICH:
                from rich.prompt import Prompt
                choice = int(Prompt.ask("[yellow]Chọn số thứ tự khách hàng"))
            else:
                choice = int(input(self.center_text("\nChọn số thứ tự khách hàng: ")))
                
            if choice < 1 or choice > len(khach_hang_list):
                if HAS_RICH:
                    from rich.panel import Panel
                    from rich.align import Align
                    console.print(Align.center(
                        Panel(
                            "[bold red]Lựa chọn không hợp lệ!",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=40
                        )
                    ))
                else:
                    print(self.center_text("Lựa chọn không hợp lệ!"))
                
                # Hiệu ứng nhấn Enter
                if HAS_RICH:
                    from rich.text import Text
                    from rich.align import Align
                    console.print("\n")
                    console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
                    input()
                else:
                    input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
            
            khach_hang = khach_hang_list[choice-1]
        except ValueError:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                console.print(Align.center(
                    Panel(
                        "[bold red]Vui lòng nhập một số!",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=40
                    )
                ))
            else:
                print(self.center_text("Vui lòng nhập một số!"))
            
            # Hiệu ứng nhấn Enter
            if HAS_RICH:
                from rich.text import Text
                from rich.align import Align
                console.print("\n")
                console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
                input()
            else:
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Lấy thông tin hóa đơn gần nhất (nếu có) để lấy chỉ số cũ
        hoa_don_list = self.db.get_hoa_don_by_khach_hang(khach_hang.ma_khach_hang)
        chi_so_cu = 0
        
        if hoa_don_list:
            # Sắp xếp theo thời gian để lấy hóa đơn gần nhất
            hoa_don_list.sort(key=lambda x: x.thang, reverse=True)
            chi_so_cu = hoa_don_list[0].chi_so_cuoi
            
            if HAS_RICH:
                console.print(Align.center(f"[yellow]Chỉ số điện kỳ trước: [bold white]{chi_so_cu}[/bold white]"))
            else:
                print(self.center_text(f"\nChỉ số điện kỳ trước: {chi_so_cu}"))
        
        # Nhập thông tin hóa đơn
        if HAS_RICH:
            from rich.prompt import Prompt
            thang = Prompt.ask("[yellow]Tháng hóa đơn (MM/YYYY)")
            chi_so_moi = int(Prompt.ask("[yellow]Chỉ số công tơ mới"))
        else:
            thang = input(self.center_text("Tháng hóa đơn (MM/YYYY): "))
            chi_so_moi = int(input(self.center_text("Chỉ số công tơ mới: ")))
        
        if chi_so_moi < chi_so_cu:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                console.print(Align.center(
                    Panel(
                        "[bold red]Lỗi: Chỉ số mới không thể nhỏ hơn chỉ số cũ!",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=60
                    )
                ))
                time.sleep(1.5)
                return
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Lỗi: Chỉ số mới không thể nhỏ hơn chỉ số cũ!{RESET}"))
                time.sleep(1.5)
                return
        
        try:
            pass  # Tiếp tục xử lý
        except ValueError:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold red]Vui lòng nhập một số hợp lệ!",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=60
                    )
                ))
                time.sleep(1.5)
                return
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Vui lòng nhập một số hợp lệ!{RESET}"))
                time.sleep(1.5)
                return
        else:
            try:
                so_luong = int(input(self.center_text("Nhập số lượng khách hàng muốn hiển thị: ")))
                if so_luong <= 0:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Số lượng phải lớn hơn 0!{RESET}"))
                    input(self.center_text("\nNhấn Enter để tiếp tục..."))
                    return
            except ValueError:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Vui lòng nhập một số!{RESET}"))
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
            
            # Yêu cầu người dùng nhập tháng (tùy chọn)
            thang = input(self.center_text("Nhập tháng (MM/YYYY) hoặc để trống để xem tất cả: "))
        
        # Hiệu ứng loading
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm dữ liệu..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tìm kiếm dữ liệu..."))
            time.sleep(0.8)
        
        # Lấy danh sách hóa đơn
        if thang:
            hoa_don_list = self.db.search_hoa_don_by_thang(thang)
        else:
            hoa_don_list = self.db.get_all_hoa_don()
        
        if not hoa_don_list:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold yellow]Không có dữ liệu hóa đơn phù hợp!",
                        border_style="yellow",
                        title="[bold yellow]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.YELLOW if HAS_COLORAMA else ''}Không có dữ liệu hóa đơn phù hợp!{RESET}"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Tính tổng tiêu thụ của từng khách hàng
        tieu_thu_khach_hang = {}
        
        for hd in hoa_don_list:
            ma_kh = hd.ma_khach_hang
            tieu_thu = hd.chi_so_cuoi - hd.chi_so_dau
            
            if ma_kh in tieu_thu_khach_hang:
                tieu_thu_khach_hang[ma_kh]["tieu_thu"] += tieu_thu
                tieu_thu_khach_hang[ma_kh]["so_hoa_don"] += 1
                tieu_thu_khach_hang[ma_kh]["thanh_tien"] += hd.so_tien
            else:
                khach_hang = self.db.get_khach_hang(ma_kh)
                ho_ten = khach_hang.ho_ten if khach_hang else "Không xác định"
                
                tieu_thu_khach_hang[ma_kh] = {
                    "ho_ten": ho_ten,
                    "tieu_thu": tieu_thu,
                    "so_hoa_don": 1,
                    "thanh_tien": hd.so_tien
                }
        
        # Sắp xếp khách hàng theo mức tiêu thụ giảm dần
        kh_sorted = sorted(tieu_thu_khach_hang.items(), key=lambda x: x[1]["tieu_thu"], reverse=True)
        
        # Giới hạn số lượng khách hàng hiển thị
        kh_top = kh_sorted[:so_luong]
        
        # Tính thống kê tổng quát
        tong_khach_hang = len(tieu_thu_khach_hang)
        tong_tieu_thu = sum(info["tieu_thu"] for _, info in kh_sorted)
        tong_tien = sum(info["thanh_tien"] for _, info in kh_sorted)
        
        # Tính phần trăm tiêu thụ của top khách hàng so với tổng
        phan_tram_tieu_thu = sum(info["tieu_thu"] for _, info in kh_top) / tong_tieu_thu * 100 if tong_tieu_thu > 0 else 0
        phan_tram_tien = sum(info["thanh_tien"] for _, info in kh_top) / tong_tien * 100 if tong_tien > 0 else 0
        
        # Hiển thị kết quả
        if HAS_RICH:
            # Hiển thị thông tin tổng quan
            summary_table = Table(show_header=False, box=None)
            summary_table.add_column("Chỉ tiêu", style="yellow")
            summary_table.add_column("Giá trị", style="cyan")
            
            summary_table.add_row("Tổng số khách hàng", f"{tong_khach_hang:,}")
            summary_table.add_row("Tổng tiêu thụ", f"{tong_tieu_thu:,} kWh")
            summary_table.add_row("Tổng tiền", f"{tong_tien:,}đ")
            summary_table.add_row(f"Tỷ lệ tiêu thụ của Top {len(kh_top)}", f"{phan_tram_tieu_thu:.2f}%")
            summary_table.add_row(f"Tỷ lệ doanh thu của Top {len(kh_top)}", f"{phan_tram_tien:.2f}%")
            
            title = f"BÁO CÁO TOP {len(kh_top)} KHÁCH HÀNG TIÊU THỤ NHIỀU NHẤT"
            if thang:
                title += f" (THÁNG {thang})"
            
            console.print(Align.center(
                Panel(
                    summary_table,
                    title=f"[bold yellow]{title}",
                    border_style="yellow",
                    width=70
                )
            ))
            
            # Hiển thị bảng chi tiết
            detail_table = Table(
                title="CHI TIẾT TIÊU THỤ",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow"
            )
            
            detail_table.add_column("STT", style="dim", width=5, justify="center")
            detail_table.add_column("Mã KH", style="cyan", width=15)
            detail_table.add_column("Họ tên", style="white")
            detail_table.add_column("Tiêu thụ (kWh)", justify="right")
            detail_table.add_column("Thành tiền", justify="right", style="green")
            detail_table.add_column("Số HĐ", justify="center")
            detail_table.add_column("% Tiêu thụ", justify="right")
            
            for i, (ma_kh, info) in enumerate(kh_top):
                # Tính phần trăm tiêu thụ so với tổng
                phan_tram = info["tieu_thu"] / tong_tieu_thu * 100 if tong_tieu_thu > 0 else 0
                
                # Hiển thị dữ liệu với màu sắc
                detail_table.add_row(
                    str(i + 1),
                    ma_kh,
                    info["ho_ten"],
                    f"{info['tieu_thu']:,}",
                    f"{info['thanh_tien']:,}đ",
                    str(info["so_hoa_don"]),
                    f"{phan_tram:.2f}%"
                )
            
            console.print(Align.center(detail_table))
            
            # Thêm ghi chú
            console.print()
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
        else:
            # Hiển thị thông tin cho terminal thường
            title = f"TOP {len(kh_top)} KHÁCH HÀNG TIÊU THỤ NHIỀU NHẤT"
            if thang:
                title += f" THÁNG {thang}"
                
            print(self.center_text(f"{MAIN_COLOR}{title}{RESET}"))
            print(self.center_text("-" * 60))
            
            # Hiển thị thông tin tổng quan
            print(self.center_text(f"• Tổng số khách hàng: {tong_khach_hang:,}"))
            print(self.center_text(f"• Tổng tiêu thụ: {tong_tieu_thu:,} kWh"))
            print(self.center_text(f"• Tổng tiền: {tong_tien:,}đ"))
            print(self.center_text(f"• Tỷ lệ tiêu thụ của Top {len(kh_top)}: {phan_tram_tieu_thu:.2f}%"))
            print(self.center_text(f"• Tỷ lệ doanh thu của Top {len(kh_top)}: {phan_tram_tien:.2f}%"))
            print()
            
            # Hiển thị chi tiết
            headers = [f"{MAIN_COLOR}STT{RESET}", f"{MAIN_COLOR}Mã KH{RESET}", f"{MAIN_COLOR}Họ tên{RESET}", 
                    f"{MAIN_COLOR}Tiêu thụ (kWh){RESET}", f"{MAIN_COLOR}Thành tiền{RESET}", f"{MAIN_COLOR}Số HĐ{RESET}", f"{MAIN_COLOR}% Tiêu thụ{RESET}"]
            data = []
            
            for i, (ma_kh, info) in enumerate(kh_top):
                # Tính phần trăm tiêu thụ so với tổng
                phan_tram = info["tieu_thu"] / tong_tieu_thu * 100 if tong_tieu_thu > 0 else 0
                
                # Thêm dữ liệu vào bảng
                data.append([
                    i + 1,
                    ma_kh,
                    info["ho_ten"],
                    f"{info['tieu_thu']:,}",
                    f"{info['thanh_tien']:,}đ",
                    info["so_hoa_don"],
                    f"{phan_tram:.2f}%"
                ])
            
            # Hiển thị bảng căn giữa
            table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
            for line in table.split('\n'):
                print(self.center_text(line))
        
        input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def bao_cao_hoa_don_chua_thanh_toan(self):
        self.clear_screen()
        
        # Hiển thị tiêu đề
        self.display_centered_title("BÁO CÁO HÓA ĐƠN CHƯA THANH TOÁN", 60)
        
        # Hiệu ứng loading
        if HAS_RICH:
            from rich.align import Align
            from rich.panel import Panel
            from rich.text import Text
            from rich.table import Table
            from rich.progress import Progress, SpinnerColumn, TextColumn
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm dữ liệu..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang lấy danh sách hóa đơn chưa thanh toán..."))
            time.sleep(0.8)
        
        # Lấy danh sách tất cả hóa đơn
        hoa_don_list = self.db.get_all_hoa_don()
        
        # Lọc ra các hóa đơn chưa thanh toán
        hoa_don_chua_tt = [hd for hd in hoa_don_list if not hd.da_thanh_toan]
        
        if not hoa_don_chua_tt:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold green]Không có hóa đơn nào chưa thanh toán!",
                        border_style="green",
                        title="[bold green]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.GREEN if HAS_COLORAMA else ''}Không có hóa đơn nào chưa thanh toán!{RESET}"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Sắp xếp theo tháng (từ cũ đến mới)
        hoa_don_chua_tt.sort(key=lambda x: (x.nam, x.thang))
        
        # Tính thống kê
        tong_so_hd = len(hoa_don_chua_tt)
        tong_tien_chua_tt = sum(hd.so_tien for hd in hoa_don_chua_tt)
        
        # Phân loại theo thời gian nợ
        today = datetime.datetime.now()
        no_duoi_30_ngay = []
        no_30_60_ngay = []
        no_60_90_ngay = []
        no_tren_90_ngay = []
        
        for hd in hoa_don_chua_tt:
            # Tạo ngày đầu tiên của tháng hóa đơn để tính số ngày quá hạn
            ngay_hoa_don = datetime.datetime(hd.nam, hd.thang, 1)
            so_ngay_no = (today - ngay_hoa_don).days
            
            if so_ngay_no <= 30:
                no_duoi_30_ngay.append(hd)
            elif so_ngay_no <= 60:
                no_30_60_ngay.append(hd)
            elif so_ngay_no <= 90:
                no_60_90_ngay.append(hd)
            else:
                no_tren_90_ngay.append(hd)
        
        # Hiển thị thống kê
        if HAS_RICH:
            # Hiển thị thông tin tổng quan
            summary_table = Table(show_header=False, box=None)
            summary_table.add_column("Chỉ tiêu", style="yellow")
            summary_table.add_column("Giá trị", style="cyan")
            
            summary_table.add_row("Tổng số hóa đơn chưa thanh toán", f"{tong_so_hd:,}")
            summary_table.add_row("Tổng số tiền chưa thu", f"{tong_tien_chua_tt:,}đ")
            
            console.print(Align.center(
                Panel(
                    summary_table,
                    title="[bold yellow]THỐNG KÊ NỢ ĐỌNG",
                    border_style="yellow",
                    width=70
                )
            ))
            
            # Hiển thị bảng phân loại theo thời gian nợ
            timing_table = Table(
                title="PHÂN LOẠI THEO THỜI GIAN NỢ",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow"
            )
            
            timing_table.add_column("Thời gian", style="white")
            timing_table.add_column("Số lượng", justify="right")
            timing_table.add_column("Số tiền", justify="right", style="green")
            timing_table.add_column("Tỷ lệ", justify="right")
            
            # Dưới 30 ngày
            sl_no_duoi_30 = len(no_duoi_30_ngay)
            tien_no_duoi_30 = sum(hd.so_tien for hd in no_duoi_30_ngay)
            tl_no_duoi_30 = sl_no_duoi_30 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_table.add_row(
                "Dưới 30 ngày",
                f"{sl_no_duoi_30}",
                f"{tien_no_duoi_30:,}đ",
                f"{tl_no_duoi_30:.2f}%"
            )
            
            # Từ 30-60 ngày
            sl_no_30_60 = len(no_30_60_ngay)
            tien_no_30_60 = sum(hd.so_tien for hd in no_30_60_ngay)
            tl_no_30_60 = sl_no_30_60 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_table.add_row(
                "30-60 ngày",
                f"{sl_no_30_60}",
                f"{tien_no_30_60:,}đ",
                f"{tl_no_30_60:.2f}%"
            )
            
            # Từ 60-90 ngày
            sl_no_60_90 = len(no_60_90_ngay)
            tien_no_60_90 = sum(hd.so_tien for hd in no_60_90_ngay)
            tl_no_60_90 = sl_no_60_90 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_table.add_row(
                "60-90 ngày",
                f"{sl_no_60_90}",
                f"{tien_no_60_90:,}đ",
                f"{tl_no_60_90:.2f}%"
            )
            
            # Trên 90 ngày
            sl_no_tren_90 = len(no_tren_90_ngay)
            tien_no_tren_90 = sum(hd.so_tien for hd in no_tren_90_ngay)
            tl_no_tren_90 = sl_no_tren_90 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_table.add_row(
                "Trên 90 ngày",
                f"{sl_no_tren_90}",
                f"{tien_no_tren_90:,}đ",
                f"{tl_no_tren_90:.2f}%"
            )
            
            console.print(Align.center(timing_table))
            
            # Hiển thị chi tiết hóa đơn chưa thanh toán
            detail_table = Table(
                title="CHI TIẾT HÓA ĐƠN CHƯA THANH TOÁN",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow"
            )
            
            detail_table.add_column("Mã HĐ", style="dim")
            detail_table.add_column("Khách hàng", style="white")
            detail_table.add_column("Tháng", justify="center")
            detail_table.add_column("Tiêu thụ (kWh)", justify="right")
            detail_table.add_column("Thành tiền", justify="right", style="green")
            detail_table.add_column("Số ngày nợ", justify="center", style="red")
            
            for hd in hoa_don_chua_tt:
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                ho_ten = khach_hang.ho_ten if khach_hang else "Không xác định"
                tieu_thu = hd.chi_so_cuoi - hd.chi_so_dau
                
                # Tính số ngày nợ
                ngay_hoa_don = datetime.datetime(hd.nam, hd.thang, 1)
                so_ngay_no = (today - ngay_hoa_don).days
                
                # Đánh dấu màu cho số ngày nợ
                style = "green"
                if so_ngay_no > 90:
                    style = "red"
                elif so_ngay_no > 60:
                    style = "orange3"
                elif so_ngay_no > 30:
                    style = "yellow"
                
                detail_table.add_row(
                    hd.ma_hoa_don,
                    ho_ten,
                    f"{hd.thang}/{hd.nam}",
                    f"{tieu_thu:,}",
                    f"{hd.so_tien:,}đ",
                    f"[{style}]{so_ngay_no}[/{style}]"
                )
            
            console.print(Align.center(detail_table))
            
            # Thêm ghi chú
            console.print()
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
        else:
            # Hiển thị thông tin cho terminal thường
            print(self.center_text(f"{MAIN_COLOR}THỐNG KÊ NỢ ĐỌNG{RESET}"))
            print(self.center_text("-" * 50))
            print(self.center_text(f"Tổng số hóa đơn chưa thanh toán: {tong_so_hd:,}"))
            print(self.center_text(f"Tổng số tiền chưa thu: {tong_tien_chua_tt:,}đ"))
            print()
            
            # Hiển thị phân loại theo thời gian nợ
            print(self.center_text(f"{MAIN_COLOR}PHÂN LOẠI THEO THỜI GIAN NỢ:{RESET}"))
            
            headers = [f"{MAIN_COLOR}Thời gian{RESET}", f"{MAIN_COLOR}Số lượng{RESET}", f"{MAIN_COLOR}Số tiền{RESET}", f"{MAIN_COLOR}Tỷ lệ{RESET}"]
            timing_data = []
            
            # Dưới 30 ngày
            sl_no_duoi_30 = len(no_duoi_30_ngay)
            tien_no_duoi_30 = sum(hd.so_tien for hd in no_duoi_30_ngay)
            tl_no_duoi_30 = sl_no_duoi_30 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_data.append(["Dưới 30 ngày", sl_no_duoi_30, f"{tien_no_duoi_30:,}đ", f"{tl_no_duoi_30:.2f}%"])
            
            # Từ 30-60 ngày
            sl_no_30_60 = len(no_30_60_ngay)
            tien_no_30_60 = sum(hd.so_tien for hd in no_30_60_ngay)
            tl_no_30_60 = sl_no_30_60 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_data.append(["30-60 ngày", sl_no_30_60, f"{tien_no_30_60:,}đ", f"{tl_no_30_60:.2f}%"])
            
            # Từ 60-90 ngày
            sl_no_60_90 = len(no_60_90_ngay)
            tien_no_60_90 = sum(hd.so_tien for hd in no_60_90_ngay)
            tl_no_60_90 = sl_no_60_90 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_data.append(["60-90 ngày", sl_no_60_90, f"{tien_no_60_90:,}đ", f"{tl_no_60_90:.2f}%"])
            
            # Trên 90 ngày
            sl_no_tren_90 = len(no_tren_90_ngay)
            tien_no_tren_90 = sum(hd.so_tien for hd in no_tren_90_ngay)
            tl_no_tren_90 = sl_no_tren_90 / tong_so_hd * 100 if tong_so_hd > 0 else 0
            timing_data.append(["Trên 90 ngày", sl_no_tren_90, f"{tien_no_tren_90:,}đ", f"{tl_no_tren_90:.2f}%"])
            
            # Hiển thị bảng căn giữa
            timing_table = tabulate(timing_data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
            for line in timing_table.split('\n'):
                print(self.center_text(line))
            
            print()
            print(self.center_text(f"{MAIN_COLOR}CHI TIẾT HÓA ĐƠN CHƯA THANH TOÁN:{RESET}"))
            
            # Hiển thị chi tiết
            headers = [f"{MAIN_COLOR}Mã HĐ{RESET}", f"{MAIN_COLOR}Khách hàng{RESET}", f"{MAIN_COLOR}Tháng{RESET}", 
                     f"{MAIN_COLOR}Tiêu thụ (kWh){RESET}", f"{MAIN_COLOR}Thành tiền (VNĐ){RESET}", f"{MAIN_COLOR}Số ngày nợ{RESET}"]
            data = []
            
            for hd in hoa_don_chua_tt:
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                ho_ten = khach_hang.ho_ten if khach_hang else "Không xác định"
                tieu_thu = hd.chi_so_cuoi - hd.chi_so_dau
                
                # Tính số ngày nợ
                ngay_hoa_don = datetime.datetime(hd.nam, hd.thang, 1)
                so_ngay_no = (today - ngay_hoa_don).days
                
                # Đánh dấu màu cho số ngày nợ
                if HAS_COLORAMA:
                    if so_ngay_no > 90:
                        so_ngay_no_str = f"{Fore.RED}{so_ngay_no}{RESET}"
                    elif so_ngay_no > 60:
                        so_ngay_no_str = f"{Fore.YELLOW}{so_ngay_no}{RESET}"
                    elif so_ngay_no > 30:
                        so_ngay_no_str = f"{Fore.BLUE}{so_ngay_no}{RESET}"
                    else:
                        so_ngay_no_str = f"{Fore.GREEN}{so_ngay_no}{RESET}"
                else:
                    so_ngay_no_str = str(so_ngay_no)
                
                data.append([
                    hd.ma_hoa_don,
                    f"{ho_ten} ({hd.ma_khach_hang})",
                    f"{hd.thang}/{hd.nam}",
                    f"{tieu_thu:,}",
                    f"{hd.so_tien:,}",
                    so_ngay_no_str
                ])
            
            # Hiển thị bảng căn giữa
            table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
            for line in table.split('\n'):
                print(self.center_text(line))
        
        input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def startup_animation(self):
        """Hiển thị hiệu ứng khởi động đẹp mắt khi mở ứng dụng"""
        self.clear_screen()
        
        if HAS_RICH:
            from rich.align import Align
            from rich.text import Text
            from rich.console import Group
            from rich.panel import Panel
            from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
            
            # Hiệu ứng màn hình chào mừng
            welcome_text = Text("CHÀO MỪNG ĐẾN VỚI", style="bold white")
            vtn_text = Text("VTN VIP", style="bold yellow")
            slogan_text = Text("QUẢN LÝ ĐIỆN NĂNG CHUYÊN NGHIỆP", style="italic yellow")
            
            # Hiệu ứng hiển thị từng dòng
            console.print()
            console.print()
            console.print(Align.center(welcome_text))
            time.sleep(0.5)
            console.print(Align.center(vtn_text))
            time.sleep(0.5)
            console.print(Align.center(slogan_text))
            time.sleep(0.8)
            
            # Hiệu ứng đường viền
            console.print()
            for i in range(60):
                border = "═" * i
                console.print(Align.center(Text(border, style="yellow")), end="\r")
                time.sleep(0.01)
            console.print()
            
            # Hiệu ứng loading với nhiều thành phần
            console.print()
            with Progress(
                "[progress.description]{task.description}",
                SpinnerColumn(),
                BarColumn(bar_width=40),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeRemainingColumn(),
                console=console,
                transient=True,
            ) as progress:
                task1 = progress.add_task("[yellow]Khởi động hệ thống...", total=100)
                task2 = progress.add_task("[cyan]Kết nối cơ sở dữ liệu...", total=100)
                task3 = progress.add_task("[green]Chuẩn bị giao diện...", total=100)
                
                for _ in range(100):
                    progress.update(task1, advance=1)
                    if _ > 20:
                        progress.update(task2, advance=1.2)
                    if _ > 50:
                        progress.update(task3, advance=2)
                    time.sleep(0.03)
            
            # Hiệu ứng hoàn thành
            console.print()
            console.print(Align.center(Text("✅ Khởi động hoàn tất!", style="bold green")))
            time.sleep(0.5)
            console.print(Align.center(Text("Đang chuyển đến hệ thống...", style="yellow")))
            time.sleep(1)
            
        else:
            # Hiệu ứng đơn giản cho terminal không hỗ trợ rich
            width = self.terminal_width
            print()
            print()
            print(self.center_text("CHÀO MỪNG ĐẾN VỚI"))
            time.sleep(0.5)
            print(self.center_text(f"{MAIN_COLOR}VTN VIP{RESET}"))
            time.sleep(0.5)
            print(self.center_text(f"{MAIN_COLOR}QUẢN LÝ ĐIỆN NĂNG CHUYÊN NGHIỆP{RESET}"))
            print()
            
            # Hiệu ứng đường viền
            for i in range(40):
                border = "═" * i
                print(self.center_text(f"{MAIN_COLOR}{border}{RESET}"), end="\r")
                time.sleep(0.02)
            print()
            print()
            
            # Hiệu ứng loading đơn giản
            stages = ["Khởi động hệ thống", "Kết nối cơ sở dữ liệu", "Chuẩn bị giao diện"]
            for stage in stages:
                print(self.center_text(f"{stage}..."))
                for i in range(21):
                    progress = "█" * i + "░" * (20 - i)
                    percent = i * 5
                    progress_text = f"[{progress}] {percent}%"
                    print(self.center_text(progress_text), end="\r")
                    time.sleep(0.05)
                print()
            
            print()
            print(self.center_text(f"{Fore.GREEN if HAS_COLORAMA else ''}✓ Khởi động hoàn tất!{RESET}"))
            time.sleep(0.5)
            print(self.center_text(f"{MAIN_COLOR}Đang chuyển đến hệ thống...{RESET}"))
            time.sleep(1)
    
    def run(self):
        """Chạy ứng dụng quản lý điện"""
        # Hiển thị hiệu ứng khởi động
        self.startup_animation()
        
        running = True
        while running:
            running = self.current_menu()
            
        # Hiển thị thông báo kết thúc
        self.clear_screen()
        if HAS_RICH:
            from rich.align import Align
            from rich.panel import Panel
            from rich.text import Text
            
            end_content = Text()
            end_content.append("Cảm ơn bạn đã sử dụng VTN VIP!", style="bold yellow")
            end_content.append("\n\n")
            end_content.append("Hẹn gặp lại lần sau!", style="yellow")
            
            console.print()
            console.print(Align.center(
                Panel(
                    end_content,
                    border_style="yellow",
                    title="[bold yellow]THÔNG BÁO",
                    title_align="center",
                    width=60
                )
            ))
            console.print()
        else:
            # Tạo khung viền đẹp căn giữa màn hình
            width = 60
            print()
            print(self.center_text(f"{MAIN_COLOR}╔═" + "═" * (width-4) + "═╗", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + " " * (width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + f"{TITLE_STYLE}THÔNG BÁO".center(width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + " " * (width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + " " * (width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + f"{TITLE_STYLE}CẢM ƠN BẠN ĐÃ SỬ DỤNG VTN VIP!".center(width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + " " * (width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + "Hẹn gặp lại lần sau".center(width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}║" + " " * (width-2) + "║", 80))
            print(self.center_text(f"{MAIN_COLOR}╚═" + "═" * (width-4) + "═╝", 80))
            print()
            
        # Hiệu ứng kết thúc
        for i in range(5, 0, -1):
            time.sleep(0.5)
            if HAS_RICH:
                console.print(Align.center(Text(f"Tự động thoát sau {i} giây...", style="yellow")))
            else:
                print(self.center_text(f"{MAIN_COLOR}Tự động thoát sau {i} giây...{RESET}", 80), end="\r")
                
        time.sleep(0.5)
    
    def create_box_menu(self, title, menu_items, width=None):
        """Tạo menu trong khung viền đẹp, trả về danh sách các dòng để hiển thị"""
        if width is None:
            # Tính toán độ rộng hợp lý dựa trên nội dung
            max_item_width = max(len(self._strip_ansi_codes(item)) for item in menu_items)
            width = max(max_item_width + 10, len(self._strip_ansi_codes(title)) + 10)  # Thêm padding
        
        lines = []
        
        # Tạo viền trên
        lines.append(f"{MAIN_COLOR}┌" + "─" * width + "┐")
        
        # Tạo dòng tiêu đề
        title_padding = (width - len(self._strip_ansi_codes(title))) // 2
        title_line = f"{MAIN_COLOR}│" + " " * title_padding + f"{TITLE_STYLE}{title}" + " " * (width - len(self._strip_ansi_codes(title)) - title_padding) + f"{MAIN_COLOR}│"
        lines.append(title_line)
        
        # Tạo đường phân cách
        lines.append(f"{MAIN_COLOR}├" + "─" * width + "┤")
        
        # Thêm các mục menu
        for item in menu_items:
            # Loại bỏ mã màu để tính toán độ dài thực
            clean_item = self._strip_ansi_codes(item)
            padding_left = 2  # Khoảng trắng bên trái
            padding_right = width - len(clean_item) - padding_left
            
            # Đảm bảo không bị tràn
            if padding_right < 0:
                padding_right = 0
                
            # Tạo dòng menu với khoảng trống phù hợp
            menu_line = f"{MAIN_COLOR}│" + " " * padding_left + f"{item}" + " " * padding_right + f"{MAIN_COLOR}│"
            lines.append(menu_line)
        
        # Tạo viền dưới
        lines.append(f"{MAIN_COLOR}└" + "─" * width + "┘")
        
        return lines
        
    def display_centered_menu(self, title, menu_items):
        """Hiển thị menu với khung viền căn giữa màn hình"""
        lines = self.create_box_menu(title, menu_items)
        for line in lines:
            print(self.center_text(line))
        print()
    
    def create_title_box(self, title, width=50):
        """Tạo khung tiêu đề đẹp và trả về danh sách các dòng"""
        title_clean = self._strip_ansi_codes(title)
        width = max(width, len(title_clean) + 10)  # Đảm bảo đủ rộng cho tiêu đề
        
        lines = []
        lines.append(f"{MAIN_COLOR}╔═" + "═" * (width-4) + "═╗")
        
        # Tính padding để căn giữa tiêu đề
        padding = (width - 4 - len(title_clean)) // 2
        lines.append(f"{MAIN_COLOR}║ " + " " * padding + f"{TITLE_STYLE}{title}" + " " * (width - 4 - len(title_clean) - padding) + f" ║")
        
        lines.append(f"{MAIN_COLOR}╚═" + "═" * (width-4) + "═╝")
        return lines
        
    def display_centered_title(self, title, width=50):
        """Hiển thị tiêu đề trong khung đẹp, căn giữa màn hình"""
        lines = self.create_title_box(title, width)
        for line in lines:
            print(self.center_text(line))
        print()
    
    def xuat_hoa_don(self):
        """Xuất hóa đơn PDF cho một khách hàng"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        if HAS_RICH:
            from rich.panel import Panel
            from rich.align import Align
            
            console.print(Align.center(
                Panel(
                    "",
                    title="[bold yellow]XUẤT HÓA ĐƠN PDF[/bold yellow]",
                    title_align="center",
                    border_style="yellow",
                    width=60
                )
            ))
        else:
            self.display_centered_title("XUẤT HÓA ĐƠN PDF", 50)
        
        # Lấy danh sách hóa đơn
        hoa_don_list = self.db.get_all_hoa_don()
        
        if not hoa_don_list:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                
                console.print(Align.center(
                    Panel(
                        "[bold red]Chưa có hóa đơn nào trong hệ thống![/bold red]",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Chưa có hóa đơn nào trong hệ thống!{RESET}"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Hiển thị danh sách hóa đơn
        if HAS_RICH:
            from rich.table import Table
            from rich.align import Align
            
            table = Table(
                title="DANH SÁCH HÓA ĐƠN",
                show_header=True,
                header_style="bold yellow",
                border_style="yellow"
            )
            
            table.add_column("STT", style="dim", width=5, justify="center")
            table.add_column("Mã HĐ", style="cyan", width=10)
            table.add_column("Khách hàng", style="white")
            table.add_column("Thời gian", width=12, justify="center")
            table.add_column("Tiêu thụ (kWh)", width=12, justify="right")
            table.add_column("Thành tiền", width=15, justify="right", style="green")
            table.add_column("Trạng thái", width=15)
            
            for i, hd in enumerate(hoa_don_list):
                # Lấy thông tin khách hàng
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                khach_hang_name = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
                
                # Định dạng tháng/năm
                thoi_gian_str = f"{hd.thang}/{hd.nam}"
                
                # Định dạng tiền
                thanh_tien_str = f"{hd.so_tien:,}đ".replace(",", ".")
                
                # Định dạng trạng thái
                trang_thai = "[green]✅ Đã thanh toán[/green]" if hd.da_thanh_toan else "[red]❌ Chưa thanh toán[/red]"
                
                # Tiêu thụ
                tieu_thu = hd.tieu_thu if hasattr(hd, 'tieu_thu') and hd.tieu_thu is not None else hd.chi_so_cuoi - hd.chi_so_dau
                
                table.add_row(
                    str(i+1),
                    hd.ma_hoa_don,
                    khach_hang_name,
                    thoi_gian_str,
                    f"{tieu_thu:,}",
                    thanh_tien_str,
                    trang_thai
                )
            
            console.print(Align.center(table))
        else:
            print(self.center_text("DANH SÁCH HÓA ĐƠN:"))
            headers = ["STT", "Mã HĐ", "Khách hàng", "Thời gian", "Tiêu thụ (kWh)", "Thành tiền", "Trạng thái"]
            data = []
            
            for i, hd in enumerate(hoa_don_list):
                # Lấy thông tin khách hàng
                khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                khach_hang_name = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
                
                # Định dạng tháng/năm
                thoi_gian_str = f"{hd.thang}/{hd.nam}"
                
                # Định dạng tiền
                thanh_tien_str = f"{hd.so_tien:,}đ".replace(",", ".")
                
                # Định dạng trạng thái
                trang_thai = "Đã thanh toán" if hd.da_thanh_toan else "Chưa thanh toán"
                
                # Tiêu thụ
                tieu_thu = hd.tieu_thu if hasattr(hd, 'tieu_thu') and hd.tieu_thu is not None else hd.chi_so_cuoi - hd.chi_so_dau
                
                data.append([
                    i+1,
                    hd.ma_hoa_don,
                    khach_hang_name,
                    thoi_gian_str,
                    f"{tieu_thu:,}",
                    thanh_tien_str,
                    trang_thai
                ])
            
            # Thêm màu cho trạng thái thanh toán
            if HAS_COLORAMA:
                for i, row in enumerate(data):
                    if "Đã thanh toán" in row[-1]:
                        data[i][-1] = f"{Fore.GREEN}✅ Đã thanh toán{RESET}"
                    else:
                        data[i][-1] = f"{Fore.RED}❌ Chưa thanh toán{RESET}"
            
            # Hiển thị bảng
            table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
            for line in table.split('\n'):
                print(self.center_text(line))
        
        # Chọn hóa đơn để xuất
        try:
            if HAS_RICH:
                from rich.prompt import Prompt
                choice = int(Prompt.ask("[yellow]Chọn STT hóa đơn để xuất PDF"))
            else:
                choice = int(input(self.center_text("\nChọn STT hóa đơn để xuất PDF: ")))
                
            if choice < 1 or choice > len(hoa_don_list):
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Lựa chọn không hợp lệ![/bold red]",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=40
                        )
                    ))
                else:
                    print(self.center_text("Lựa chọn không hợp lệ!"))
                
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
            
            # Lấy hóa đơn được chọn
            hoa_don = hoa_don_list[choice-1]
            
            # Lấy thông tin khách hàng
            khach_hang = self.db.get_khach_hang(hoa_don.ma_khach_hang)
            if not khach_hang:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Không tìm thấy thông tin khách hàng![/bold red]",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=50
                        )
                    ))
                else:
                    print(self.center_text("Không tìm thấy thông tin khách hàng!"))
                
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
            
            # Lấy bảng giá
            bang_gia = self.db.get_bang_gia_active()
            if not bang_gia:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Không tìm thấy bảng giá điện![/bold red]",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=50
                        )
                    ))
                else:
                    print(self.center_text("Không tìm thấy bảng giá điện!"))
                
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
            
            # Hiệu ứng loading khi xuất file
            if HAS_RICH:
                from rich.progress import Progress, TextColumn, BarColumn, SpinnerColumn
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold yellow]Đang xuất hóa đơn PDF...[/bold yellow]"),
                    BarColumn(bar_width=40),
                    TextColumn("[bold yellow]{task.percentage:.0f}%[/bold yellow]"),
                    expand=False,
                    transient=True,
                ) as progress:
                    task = progress.add_task("[yellow]Đang xuất...", total=100)
                    
                    # Tạo các bước để tăng progress bar
                    for i in range(101):
                        time.sleep(0.01)
                        progress.update(task, completed=i)
                        
                        # Thực hiện xuất PDF khi đến 50%
                        if i == 50:
                            try:
                                # Import hàm tạo hóa đơn PDF
                                from models.hoa_don_pdf import tao_hoa_don_pdf
                                
                                # Xuất hóa đơn PDF
                                pdf_path = tao_hoa_don_pdf(hoa_don, khach_hang, bang_gia)
                            except Exception as e:
                                pdf_path = None
                                error_msg = str(e)
            else:
                # Hiệu ứng loading đơn giản
                print(self.center_text("Đang xuất hóa đơn PDF..."))
                time.sleep(1)
                
                try:
                    # Import hàm tạo hóa đơn PDF
                    from models.hoa_don_pdf import tao_hoa_don_pdf
                    
                    # Xuất hóa đơn PDF
                    pdf_path = tao_hoa_don_pdf(hoa_don, khach_hang, bang_gia)
                except Exception as e:
                    pdf_path = None
                    error_msg = str(e)
            
            # Hiển thị kết quả
            if pdf_path:
                if HAS_RICH:
                    from rich.text import Text
                    
                    success_panel = Panel(
                        Text.from_markup(
                            f"[green]✓[/green] Đã xuất hóa đơn PDF thành công!\n\n"
                            f"[bold]Mã hóa đơn:[/bold] [cyan]{hoa_don.ma_hoa_don}[/cyan]\n"
                            f"[bold]Khách hàng:[/bold] [cyan]{khach_hang.ho_ten}[/cyan]\n"
                            f"[bold]Vị trí file:[/bold] [cyan]{pdf_path}[/cyan]"
                        ),
                        title="[bold green]THÀNH CÔNG[/bold green]",
                        border_style="green",
                        width=70
                    )
                    
                    console.print()
                    console.print(Align.center(success_panel))
                    
                    # Hỏi xem có muốn mở file PDF không
                    open_pdf = Prompt.ask(
                        "[yellow]Bạn có muốn mở file PDF không?[/yellow]",
                        choices=["y", "n"],
                        default="y"
                    )
                    
                    if open_pdf.lower() == "y":
                        try:
                            import os
                            import platform
                            import subprocess
                            
                            if platform.system() == 'Windows':
                                os.startfile(pdf_path)
                            elif platform.system() == 'Darwin':  # macOS
                                subprocess.run(['open', pdf_path])
                            else:  # Linux
                                subprocess.run(['xdg-open', pdf_path])
                        except Exception as e:
                            console.print(f"[red]Không thể mở file: {str(e)}[/red]")
                else:
                    print(self.center_text(f"{Fore.GREEN if HAS_COLORAMA else ''}✅ Đã xuất hóa đơn PDF thành công!{RESET}"))
                    print(self.center_text(f"Mã hóa đơn: {hoa_don.ma_hoa_don}"))
                    print(self.center_text(f"Khách hàng: {khach_hang.ho_ten}"))
                    print(self.center_text(f"Vị trí file: {pdf_path}"))
                    
                    # Hỏi xem có muốn mở file PDF không
                    open_pdf = input(self.center_text("\nBạn có muốn mở file PDF không? (y/n): "))
                    
                    if open_pdf.lower() == "y":
                        try:
                            import os
                            import platform
                            import subprocess
                            
                            if platform.system() == 'Windows':
                                os.startfile(pdf_path)
                            elif platform.system() == 'Darwin':  # macOS
                                subprocess.run(['open', pdf_path])
                            else:  # Linux
                                subprocess.run(['xdg-open', pdf_path])
                        except Exception as e:
                            print(self.center_text(f"Không thể mở file: {str(e)}"))
            else:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            f"[bold red]Lỗi khi xuất hóa đơn PDF: {error_msg}[/bold red]",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=70
                        )
                    ))
                else:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Lỗi khi xuất hóa đơn PDF: {error_msg}{RESET}"))
            
        except ValueError:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold red]Vui lòng nhập một số![/bold red]",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=40
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Vui lòng nhập một số!{RESET}"))
        except Exception as e:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        f"[bold red]Lỗi: {str(e)}[/bold red]",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=50
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Lỗi: {str(e)}{RESET}"))
        
        # Hiệu ứng nhấn Enter để tiếp tục
        if HAS_RICH:
            from rich.text import Text
            console.print("\n")
            console.print(Align.center(Text("Nhấn Enter để tiếp tục...", style="italic yellow")))
            input()
        else:
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def cap_nhat_hoa_don(self):
        """Cập nhật thông tin hóa đơn"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        if HAS_RICH:
            from rich.panel import Panel
            from rich.align import Align
            from rich.text import Text
            
            console.print(Align.center(
                Panel(
                    "",
                    title="[bold yellow]CẬP NHẬT HÓA ĐƠN[/bold yellow]",
                    title_align="center",
                    
                    border_style="yellow",
                    width=60
                )
            ))
        else:
            self.display_centered_title("CẬP NHẬT HÓA ĐƠN", 50)
        
        # Yêu cầu người dùng nhập mã hóa đơn
        if HAS_RICH:
            from rich.prompt import Prompt
            ma_hoa_don = Prompt.ask("[bold yellow]Nhập mã hóa đơn cần cập nhật", console=console)
        else:
            ma_hoa_don = input(self.center_text("Nhập mã hóa đơn cần cập nhật: "))
        
        # Hiệu ứng loading
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm hóa đơn..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tìm kiếm hóa đơn..."))
            time.sleep(0.8)
        
        # Tìm hóa đơn
        hoa_don = self.db.get_hoa_don(ma_hoa_don)
        
        if not hoa_don:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                
                console.print(Align.center(
                    Panel(
                        f"[bold red]Không tìm thấy hóa đơn với mã [white]{ma_hoa_don}[/white]!",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Không tìm thấy hóa đơn với mã {ma_hoa_don}!{RESET}"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Lấy thông tin khách hàng
        khach_hang = self.db.get_khach_hang(hoa_don.ma_khach_hang)
        ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
        
        # Hiển thị thông tin hiện tại
        if HAS_RICH:
            from rich.table import Table
            from rich.align import Align
            
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Thuộc tính", style="yellow")
            info_table.add_column("Giá trị", style="white")
            
            info_table.add_row("Mã hóa đơn", hoa_don.ma_hoa_don)
            info_table.add_row("Khách hàng", f"{ten_khach_hang} ({hoa_don.ma_khach_hang})")
            info_table.add_row("Tháng/Năm", f"{hoa_don.thang}/{hoa_don.nam}")
            info_table.add_row("Chỉ số đầu", str(hoa_don.chi_so_dau))
            info_table.add_row("Chỉ số cuối", str(hoa_don.chi_so_cuoi))
            info_table.add_row("Tiêu thụ", str(hoa_don.chi_so_cuoi - hoa_don.chi_so_dau))
            info_table.add_row("Thành tiền", f"{hoa_don.so_tien:,}đ".replace(",", "."))
            info_table.add_row("Đã thanh toán", "✅ Đã thanh toán" if hoa_don.da_thanh_toan else "❌ Chưa thanh toán")
            
            console.print(Align.center(
                Panel(
                    info_table,
                    title="[bold yellow]THÔNG TIN HIỆN TẠI",
                    border_style="yellow",
                    width=70
                )
            ))
            
            console.print()
            console.print(Align.center(Text("Nhập thông tin mới (để trống nếu không thay đổi)", style="bold yellow")))
            
            # Chỉ cho phép thay đổi một số thông tin
            chi_so_cuoi = Prompt.ask(
                f"[yellow]Chỉ số cuối[/yellow] [[{hoa_don.chi_so_cuoi}]]", 
                default=str(hoa_don.chi_so_cuoi),
                console=console
            )
            
            # Xác nhận thanh toán
            da_thanh_toan = Prompt.ask(
                f"[yellow]Đã thanh toán[/yellow] [[{'Có' if hoa_don.da_thanh_toan else 'Không'}]]",
                choices=["y", "n"],
                default="y" if hoa_don.da_thanh_toan else "n",
                console=console
            )
        else:
            print(self.center_text("\nThông tin hiện tại của hóa đơn:"))
            print(self.center_text(f"Mã hóa đơn: {hoa_don.ma_hoa_don}"))
            print(self.center_text(f"Khách hàng: {ten_khach_hang} ({hoa_don.ma_khach_hang})"))
            print(self.center_text(f"Tháng/Năm: {hoa_don.thang}/{hoa_don.nam}"))
            print(self.center_text(f"Chỉ số đầu: {hoa_don.chi_so_dau}"))
            print(self.center_text(f"Chỉ số cuối: {hoa_don.chi_so_cuoi}"))
            print(self.center_text(f"Tiêu thụ: {hoa_don.chi_so_cuoi - hoa_don.chi_so_dau}"))
            print(self.center_text(f"Thành tiền: {hoa_don.so_tien:,}đ".replace(",", ".")))
            print(self.center_text(f"Đã thanh toán: {'Có' if hoa_don.da_thanh_toan else 'Không'}"))
            
            print(self.center_text("\nNhập thông tin mới (để trống nếu không thay đổi):"))
            chi_so_cuoi_str = input(self.center_text(f"Chỉ số cuối [{hoa_don.chi_so_cuoi}]: "))
            chi_so_cuoi = chi_so_cuoi_str if chi_so_cuoi_str else str(hoa_don.chi_so_cuoi)
            
            da_thanh_toan_str = input(self.center_text(f"Đã thanh toán (y/n) [{'y' if hoa_don.da_thanh_toan else 'n'}]: "))
            da_thanh_toan = da_thanh_toan_str.lower() if da_thanh_toan_str else "y" if hoa_don.da_thanh_toan else "n"
        
        # Cập nhật thông tin
        try:
            chi_so_cuoi = int(chi_so_cuoi)
            if chi_so_cuoi < hoa_don.chi_so_dau:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Lỗi: Chỉ số cuối không thể nhỏ hơn chỉ số đầu!",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=60
                        )
                    ))
                else:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Lỗi: Chỉ số cuối không thể nhỏ hơn chỉ số đầu!{RESET}"))
                
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
            
            # Cập nhật đối tượng hóa đơn
            hoa_don.chi_so_cuoi = chi_so_cuoi
            hoa_don.da_thanh_toan = da_thanh_toan.lower() == "y"
            
            # Tính lại tiền điện
            bang_gia = self.db.get_bang_gia_active() or self.db.get_bang_gia_hien_hanh()
            if bang_gia:
                # Tính lại tiền điện dựa trên chỉ số mới
                dien_tieu_thu = hoa_don.chi_so_cuoi - hoa_don.chi_so_dau
                hoa_don.so_tien = bang_gia.tinh_tien_dien(dien_tieu_thu)
            
            # Hiệu ứng loading khi cập nhật
            if HAS_RICH:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold yellow]Đang cập nhật hóa đơn..."),
                    transient=True,
                ) as progress:
                    task = progress.add_task("[yellow]Đang xử lý...", total=100)
                    for i in range(101):
                        time.sleep(0.01)
                        progress.update(task, completed=i)
            else:
                print(self.center_text("Đang cập nhật hóa đơn..."))
                time.sleep(0.8)
            
            # Lưu vào cơ sở dữ liệu
            success = self.db.update_hoa_don(hoa_don)
            
            if success:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            f"[bold green]Đã cập nhật hóa đơn [white]{hoa_don.ma_hoa_don}[/white] thành công!",
                            border_style="green",
                            title="[bold green]THÀNH CÔNG",
                            width=60
                        )
                    ))
                    
                    # Hiển thị so sánh thông tin trước và sau
                    compare_table = Table(title="THÔNG TIN SAU KHI CẬP NHẬT", show_header=True, header_style="bold yellow", border_style="green")
                    compare_table.add_column("Thuộc tính", style="yellow")
                    compare_table.add_column("Giá trị", style="green")
                    
                    compare_table.add_row("Chỉ số cuối", str(hoa_don.chi_so_cuoi))
                    compare_table.add_row("Tiêu thụ", str(hoa_don.chi_so_cuoi - hoa_don.chi_so_dau))
                    compare_table.add_row("Thành tiền", f"{hoa_don.so_tien:,}đ".replace(",", "."))
                    compare_table.add_row("Đã thanh toán", "✅ Đã thanh toán" if hoa_don.da_thanh_toan else "❌ Chưa thanh toán")
                    
                    console.print(Align.center(compare_table))
                else:
                    print(self.center_text(f"\n{Fore.GREEN if HAS_COLORAMA else ''}Đã cập nhật hóa đơn {hoa_don.ma_hoa_don} thành công!{RESET}"))
                    
                    # Hiển thị thông tin đã cập nhật
                    print(self.center_text("\nThông tin sau khi cập nhật:"))
                    print(self.center_text(f"Chỉ số cuối: {hoa_don.chi_so_cuoi}"))
                    print(self.center_text(f"Tiêu thụ: {hoa_don.chi_so_cuoi - hoa_don.chi_so_dau}"))
                    print(self.center_text(f"Thành tiền: {hoa_don.so_tien:,}đ".replace(",", ".")))
                    print(self.center_text(f"Đã thanh toán: {'Có' if hoa_don.da_thanh_toan else 'Không'}"))
            else:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Cập nhật hóa đơn thất bại!",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=60
                        )
                    ))
                else:
                    print(self.center_text(f"\n{Fore.RED if HAS_COLORAMA else ''}Cập nhật hóa đơn thất bại!{RESET}"))
        except ValueError:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold red]Lỗi: Chỉ số cuối phải là một số!",
                        border_style="red",
                        title="[bold red]LỖI",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Lỗi: Chỉ số cuối phải là một số!{RESET}"))
        
        # Nhấn Enter để tiếp tục
        input(self.center_text("\nNhấn Enter để tiếp tục..."))

    def xoa_hoa_don(self):
        """Xóa hóa đơn"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        if HAS_RICH:
            from rich.panel import Panel
            from rich.align import Align
            
            console.print(Align.center(
                Panel(
                    "",
                    title="[bold yellow]XÓA HÓA ĐƠN[/bold yellow]",
                    title_align="center",
                    border_style="yellow",
                    width=60
                )
            ))
        else:
            self.display_centered_title("XÓA HÓA ĐƠN", 50)
        
        # Yêu cầu người dùng nhập mã hóa đơn
        if HAS_RICH:
            from rich.prompt import Prompt
            ma_hoa_don = Prompt.ask("[bold yellow]Nhập mã hóa đơn cần xóa", console=console)
        else:
            ma_hoa_don = input(self.center_text("Nhập mã hóa đơn cần xóa: "))
        
        # Hiệu ứng loading
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm hóa đơn..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tìm kiếm hóa đơn..."))
            time.sleep(0.8)
        
        # Tìm hóa đơn
        hoa_don = self.db.get_hoa_don(ma_hoa_don)
        
        if not hoa_don:
            if HAS_RICH:
                from rich.panel import Panel
                from rich.align import Align
                
                console.print(Align.center(
                    Panel(
                        f"[bold red]Không tìm thấy hóa đơn với mã [white]{ma_hoa_don}[/white]!",
                        border_style="red",
                        title="[bold red]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Không tìm thấy hóa đơn với mã {ma_hoa_don}!{RESET}"))
            
            input(self.center_text("\nNhấn Enter để tiếp tục..."))
            return
        
        # Lấy thông tin khách hàng
        khach_hang = self.db.get_khach_hang(hoa_don.ma_khach_hang)
        ten_khach_hang = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
        
        # Hiển thị thông tin hóa đơn
        if HAS_RICH:
            from rich.table import Table
            from rich.align import Align
            
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Thuộc tính", style="yellow")
            info_table.add_column("Giá trị", style="white")
            
            info_table.add_row("Mã hóa đơn", hoa_don.ma_hoa_don)
            info_table.add_row("Khách hàng", f"{ten_khach_hang} ({hoa_don.ma_khach_hang})")
            info_table.add_row("Tháng/Năm", f"{hoa_don.thang}/{hoa_don.nam}")
            info_table.add_row("Chỉ số đầu", str(hoa_don.chi_so_dau))
            info_table.add_row("Chỉ số cuối", str(hoa_don.chi_so_cuoi))
            info_table.add_row("Tiêu thụ", str(hoa_don.chi_so_cuoi - hoa_don.chi_so_dau))
            info_table.add_row("Thành tiền", f"{hoa_don.so_tien:,}đ".replace(",", "."))
            info_table.add_row("Đã thanh toán", "✅ Đã thanh toán" if hoa_don.da_thanh_toan else "❌ Chưa thanh toán")
            
            console.print(Align.center(
                Panel(
                    info_table,
                    title="[bold yellow]THÔNG TIN HÓA ĐƠN CẦN XÓA",
                    border_style="yellow",
                    width=70
                )
            ))
        else:
            print(self.center_text("\nThông tin hóa đơn cần xóa:"))
            print(self.center_text(f"Mã hóa đơn: {hoa_don.ma_hoa_don}"))
            print(self.center_text(f"Khách hàng: {ten_khach_hang} ({hoa_don.ma_khach_hang})"))
            print(self.center_text(f"Tháng/Năm: {hoa_don.thang}/{hoa_don.nam}"))
            print(self.center_text(f"Chỉ số đầu: {hoa_don.chi_so_dau}"))
            print(self.center_text(f"Chỉ số cuối: {hoa_don.chi_so_cuoi}"))
            print(self.center_text(f"Tiêu thụ: {hoa_don.chi_so_cuoi - hoa_don.chi_so_dau}"))
            print(self.center_text(f"Thành tiền: {hoa_don.so_tien:,}đ".replace(",", ".")))
            print(self.center_text(f"Đã thanh toán: {'Có' if hoa_don.da_thanh_toan else 'Không'}"))
        
        # Xác nhận xóa
        if HAS_RICH:
            from rich.prompt import Confirm
            confirm = Confirm.ask(
                "[bold red]Bạn có chắc muốn xóa hóa đơn này?",
                default=False,
                console=console
            )
        else:
            confirm_str = input(self.center_text("\nBạn có chắc muốn xóa hóa đơn này? (y/n): "))
            confirm = confirm_str.lower() == 'y'
        
        if confirm:
            # Hiệu ứng loading khi xóa
            if HAS_RICH:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold red]Đang xóa hóa đơn..."),
                    transient=True,
                ) as progress:
                    task = progress.add_task("[red]Đang xử lý...", total=100)
                    for i in range(101):
                        time.sleep(0.01)
                        progress.update(task, completed=i)
            else:
                print(self.center_text("Đang xóa hóa đơn..."))
                time.sleep(0.8)
            
            # Thực hiện xóa
            success = self.db.delete_hoa_don(ma_hoa_don)
            
            if success:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            f"[bold green]Đã xóa hóa đơn [white]{ma_hoa_don}[/white] thành công!",
                            border_style="green",
                            title="[bold green]THÀNH CÔNG",
                            width=60
                        )
                    ))
                else:
                    print(self.center_text(f"\n{Fore.GREEN if HAS_COLORAMA else ''}Đã xóa hóa đơn {ma_hoa_don} thành công!{RESET}"))
            else:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Xóa hóa đơn thất bại!",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=60
                        )
                    ))
                else:
                    print(self.center_text(f"\n{Fore.RED if HAS_COLORAMA else ''}Xóa hóa đơn thất bại!{RESET}"))
        else:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold yellow]Đã hủy xóa hóa đơn.",
                        border_style="yellow",
                        title="[bold yellow]THÔNG BÁO",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"\n{MAIN_COLOR if HAS_COLORAMA else ''}Đã hủy xóa hóa đơn.{RESET}"))
        
        # Nhấn Enter để tiếp tục
        input(self.center_text("\nNhấn Enter để tiếp tục..."))
    
    def tim_kiem_hoa_don(self):
        """Tìm kiếm hóa đơn"""
        self.clear_screen()
        
        # Hiển thị tiêu đề
        if HAS_RICH:
            from rich.panel import Panel
            from rich.align import Align
            
            console.print(Align.center(
                Panel(
                    "",
                    title="[bold yellow]TÌM KIẾM HÓA ĐƠN[/bold yellow]", 
                    title_align="center",
                    border_style="yellow",
                    width=60
                )
            ))
        else:
            self.display_centered_title("TÌM KIẾM HÓA ĐƠN", 50)
        
        # Hiển thị các tùy chọn tìm kiếm
        if HAS_RICH:
            from rich.prompt import Prompt
            from rich.console import Group
            from rich.panel import Panel
            from rich.align import Align
            from rich.text import Text
            from rich.table import Table
            
            options = [
                "[1] Tìm theo mã hóa đơn",
                "[2] Tìm theo tên khách hàng",
                "[3] Tìm theo tháng/năm",
                "[0] Quay lại"
            ]
            
            console.print(Align.center(
                Panel(
                    Group(*[Text(opt) for opt in options]),
                    title="[bold yellow]TÙY CHỌN TÌM KIẾM",
                    border_style="yellow",
                    width=40
                )
            ))
            
            choice = Prompt.ask(
                "[bold yellow]Nhập lựa chọn của bạn",
                choices=["0", "1", "2", "3"],
                default="1",
                console=console
            )
        else:
            print(self.center_text("TÙY CHỌN TÌM KIẾM:"))
            print(self.center_text("1. Tìm theo mã hóa đơn"))
            print(self.center_text("2. Tìm theo tên khách hàng"))
            print(self.center_text("3. Tìm theo tháng/năm"))
            print(self.center_text("0. Quay lại"))
            print()
            
            choice = input(self.center_text("Nhập lựa chọn của bạn: "))
        
        if choice == "0":
            return
        
        # Hiển thị form tìm kiếm tương ứng
        keyword = ""
        thang = None
        nam = None
        
        if choice == "1":
            # Tìm theo mã hóa đơn
            if HAS_RICH:
                keyword = Prompt.ask("[bold yellow]Nhập mã hóa đơn cần tìm", console=console)
            else:
                keyword = input(self.center_text("Nhập mã hóa đơn cần tìm: "))
        elif choice == "2":
            # Tìm theo tên khách hàng
            if HAS_RICH:
                keyword = Prompt.ask("[bold yellow]Nhập tên khách hàng cần tìm", console=console)
            else:
                keyword = input(self.center_text("Nhập tên khách hàng cần tìm: "))
        elif choice == "3":
            # Tìm theo tháng/năm
            if HAS_RICH:
                thang_nam = Prompt.ask("[bold yellow]Nhập tháng/năm (MM/YYYY)", console=console)
            else:
                thang_nam = input(self.center_text("Nhập tháng/năm (MM/YYYY): "))
            
            try:
                parts = thang_nam.split('/')
                if len(parts) == 2:
                    thang = int(parts[0])
                    nam = int(parts[1])
            except:
                if HAS_RICH:
                    console.print(Align.center(
                        Panel(
                            "[bold red]Định dạng tháng/năm không hợp lệ! Vui lòng nhập theo định dạng MM/YYYY.",
                            border_style="red",
                            title="[bold red]LỖI",
                            width=70
                        )
                    ))
                else:
                    print(self.center_text(f"{Fore.RED if HAS_COLORAMA else ''}Định dạng tháng/năm không hợp lệ! Vui lòng nhập theo định dạng MM/YYYY.{RESET}"))
                
                input(self.center_text("\nNhấn Enter để tiếp tục..."))
                return
        
        # Hiệu ứng loading
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold yellow]Đang tìm kiếm..."),
                transient=True,
            ) as progress:
                task = progress.add_task("[yellow]Đang xử lý...", total=100)
                for i in range(101):
                    time.sleep(0.01)
                    progress.update(task, completed=i)
        else:
            print(self.center_text("Đang tìm kiếm..."))
            time.sleep(0.8)
        
        # Thực hiện tìm kiếm
        if choice == "1":
            # Tìm theo mã hóa đơn
            hoa_don_list = self.db.search_hoa_don_by_ma(keyword)
        elif choice == "2":
            # Tìm theo tên khách hàng
            hoa_don_list = self.db.search_hoa_don(keyword)
        elif choice == "3":
            # Tìm theo tháng/năm
            hoa_don_list = [hd for hd in self.db.get_all_hoa_don() if hd.thang == thang and hd.nam == nam]
        
        # Hiển thị kết quả
        if not hoa_don_list:
            if HAS_RICH:
                console.print(Align.center(
                    Panel(
                        "[bold yellow]Không tìm thấy hóa đơn nào phù hợp!",
                        border_style="yellow",
                        title="[bold yellow]KẾT QUẢ TÌM KIẾM",
                        width=60
                    )
                ))
            else:
                print(self.center_text(f"{MAIN_COLOR if HAS_COLORAMA else ''}Không tìm thấy hóa đơn nào phù hợp!{RESET}"))
        else:
            if HAS_RICH:
                # Hiển thị số lượng kết quả
                console.print(Align.center(
                    Panel(
                        f"[bold green]Đã tìm thấy [white]{len(hoa_don_list)}[/white] hóa đơn phù hợp.",
                        border_style="green",
                        title="[bold green]KẾT QUẢ TÌM KIẾM",
                        width=60
                    )
                ))
                
                # Tạo bảng kết quả
                table = Table(
                    title="DANH SÁCH HÓA ĐƠN",
                    show_header=True,
                    header_style="bold yellow",
                    border_style="yellow"
                )
                
                table.add_column("STT", style="dim", width=5, justify="center")
                table.add_column("Mã HĐ", style="cyan", width=10)
                table.add_column("Khách hàng", style="white")
                table.add_column("Tháng/Năm", width=12, justify="center")
                table.add_column("Tiêu thụ (kWh)", width=12, justify="right")
                table.add_column("Thành tiền", width=15, justify="right", style="green")
                table.add_column("Trạng thái", width=15)
                
                for i, hd in enumerate(hoa_don_list):
                    # Lấy thông tin khách hàng
                    khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                    khach_hang_name = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
                    
                    # Định dạng tháng/năm
                    thoi_gian_str = f"{hd.thang}/{hd.nam}"
                    
                    # Định dạng tiền
                    thanh_tien_str = f"{hd.so_tien:,}đ".replace(",", ".")
                    
                    # Định dạng trạng thái
                    trang_thai = "[green]✅ Đã thanh toán[/green]" if hd.da_thanh_toan else "[red]❌ Chưa thanh toán[/red]"
                    
                    # Tiêu thụ
                    tieu_thu = hd.chi_so_cuoi - hd.chi_so_dau
                    
                    # Highlight từ khóa tìm kiếm nếu có
                    ma_hoa_don = hd.ma_hoa_don
                    khach_hang_name_display = khach_hang_name
                    
                    if choice in ["1", "2"] and keyword:
                        if choice == "1" and keyword.lower() in ma_hoa_don.lower():
                            ma_hoa_don = ma_hoa_don.replace(keyword, f"[bold yellow]{keyword}[/bold yellow]")
                        elif choice == "2" and keyword.lower() in khach_hang_name.lower():
                            khach_hang_name_display = khach_hang_name.replace(keyword, f"[bold yellow]{keyword}[/bold yellow]")
                    
                    table.add_row(
                        str(i+1),
                        ma_hoa_don,
                        khach_hang_name_display,
                        thoi_gian_str,
                        f"{tieu_thu:,}",
                        thanh_tien_str,
                        trang_thai
                    )
                
                console.print(Align.center(table))
            else:
                # Hiển thị danh sách kết quả cho terminal thường
                print(self.center_text(f"{MAIN_COLOR}Đã tìm thấy {len(hoa_don_list)} hóa đơn phù hợp:{RESET}"))
                print()
                
                headers = ["STT", "Mã HĐ", "Khách hàng", "Tháng/Năm", "Tiêu thụ (kWh)", "Thành tiền", "Trạng thái"]
                
                # Thêm màu cho header nếu có colorama
                if HAS_COLORAMA:
                    headers = [f"{MAIN_COLOR}{header}{RESET}" for header in headers]
                
                data = []
                for i, hd in enumerate(hoa_don_list):
                    # Lấy thông tin khách hàng
                    khach_hang = self.db.get_khach_hang(hd.ma_khach_hang)
                    khach_hang_name = khach_hang.ho_ten if khach_hang else "Không tìm thấy"
                    
                    # Định dạng tháng/năm
                    thoi_gian_str = f"{hd.thang}/{hd.nam}"
                    
                    # Định dạng tiền
                    thanh_tien_str = f"{hd.so_tien:,}đ".replace(",", ".")
                    
                    # Định dạng trạng thái
                    trang_thai = "Đã thanh toán" if hd.da_thanh_toan else "Chưa thanh toán"
                    
                    # Tiêu thụ
                    tieu_thu = hd.chi_so_cuoi - hd.chi_so_dau
                    
                    data.append([
                        i+1,
                        hd.ma_hoa_don,
                        khach_hang_name,
                        thoi_gian_str,
                        f"{tieu_thu:,}",
                        thanh_tien_str,
                        trang_thai
                    ])
                
                # Thêm màu cho trạng thái thanh toán
                if HAS_COLORAMA:
                    for i, row in enumerate(data):
                        if "Đã thanh toán" in row[-1]:
                            data[i][-1] = f"{Fore.GREEN}✅ Đã thanh toán{RESET}"
                        else:
                            data[i][-1] = f"{Fore.RED}❌ Chưa thanh toán{RESET}"
                
                # Hiển thị bảng căn giữa
                table = tabulate(data, headers=headers, tablefmt="grid", stralign="center", numalign="center")
                for line in table.split('\n'):
                    print(self.center_text(line))
        
        # Nhấn Enter để tiếp tục
        input(self.center_text("\nNhấn Enter để tiếp tục..."))

if __name__ == "__main__":
    app = QuanLyDien()
    app.run() 