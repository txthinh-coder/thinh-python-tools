import os
import win32print
import win32ui
from PIL import Image, ImageWin

def get_default_printer():
    """Lấy tên máy in mặc định trên Windows."""
    return win32print.GetDefaultPrinter()

def print_image(file_path, printer_name=None):
    """In hình ảnh với kích thước gốc, không bị méo, căn full trang."""
    if printer_name is None:
        printer_name = get_default_printer()

    hprinter = win32print.OpenPrinter(printer_name)
    pdc = win32ui.CreateDC()
    pdc.CreatePrinterDC(printer_name)

    # Mở ảnh bằng Pillow
    img = Image.open(file_path)
    img = img.convert("RGB")  # Chuyển về định dạng chuẩn

    # Lấy kích thước ảnh gốc
    img_width, img_height = img.size

    # Xác định khổ giấy A4 ngang (11.69 x 8.27 inch)
    dpi = 300  
    page_width = int(11.69 * dpi)
    page_height = int(8.27 * dpi)

    # Xác định tỷ lệ khớp giấy A4 mà không méo ảnh
    img_ratio = img_width / img_height
    page_ratio = page_width / page_height

    if img_ratio > page_ratio:
        # Ảnh rộng hơn giấy → Scale theo chiều ngang
        new_width = page_width
        new_height = int(page_width / img_ratio)
    else:
        # Ảnh cao hơn giấy → Scale theo chiều dọc
        new_height = page_height
        new_width = int(page_height * img_ratio)

    # Resize ảnh theo tỷ lệ phù hợp
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Căn giữa ảnh trên giấy
    x_offset = (page_width - new_width) // 2
    y_offset = (page_height - new_height) // 2

    # Bắt đầu tài liệu in
    pdc.StartDoc(file_path)
    pdc.StartPage()

    # In ảnh đã căn giữa
    dib = ImageWin.Dib(img)
    dib.draw(pdc.GetHandleOutput(), (x_offset, y_offset, x_offset + new_width, y_offset + new_height))

    pdc.EndPage()
    pdc.EndDoc()
    pdc.DeleteDC()

def print_all_images_in_folder(folder_path, printer_name=None):
    """Tìm và in tất cả hình ảnh trong thư mục bằng máy in mặc định."""
    if printer_name is None:
        printer_name = get_default_printer()

    image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(image_extensions)]

    if not image_files:
        print("Không tìm thấy file hình nào trong thư mục.")
        return

    for image in image_files:
        file_path = os.path.join(folder_path, image)
        print(f"Đang in: {file_path} với máy in {printer_name}")
        print_image(file_path, printer_name)