import base64
import configparser
import time
from bs4 import BeautifulSoup
from solvers.svgcaptcha import solver
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import os

# Đọc file config.ini với mã hóa UTF-8
config = configparser.ConfigParser()
with open('config.ini', 'r', encoding='utf-8') as configfile:
    config.read_file(configfile)

# Lấy giá trị ID từ file config
url = config.get('settings', 'url')
news_close_xpath = config.get('Fields', 'news_close_xpath_name')
tbketqua_xpath = config.get('Fields', 'tbketqua_xpath')
input_MST_NBan = config.get('Fields', 'input_MST_NBan')
input_KHHDon = config.get('Fields', 'input_KHHDon')
input_SHDon = config.get('Fields', 'input_SHDon')
input_TgTThue = config.get('Fields', 'input_TgTThue')
input_TgTTTBSo = config.get('Fields', 'input_TgTTTBSo')
input_captcha = config.get('Fields', 'input_captcha')
button_click = config.get('Fields', 'button_click')
select_LHDon_xpath = config.get('Fields', 'select_LHDon')
select_LHDonBH_xpath = config.get('Fields', 'select_LHDonBH')


def open_website():
    """
    Khởi tạo trình duyệt, mở trang web và trả về đối tượng driver.
    Returns:
        driver: Đối tượng WebDriver đã khởi tạo và mở trang web.
    """
    # Khởi tạo các tùy chọn trình duyệt
    options = Options()
    # options.add_argument("--headless")  # Chạy ở chế độ headless nếu cần
    options.add_argument("--log-level=3")  # Ẩn các thông báo không cần thiết

    # Đường dẫn tới chromedriver
    chromedriver_path = './chromedriver.exe' 
    service = ChromeService(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # Đặt kích thước cửa sổ trình duyệt
    driver.maximize_window()
    
    # Mở trang web
    #url = 'https://hoadondientu.gdt.gov.vn/'
    #driver.get(url)

    # Thay đổi tỷ lệ zoom của trang web
    zoom_level = 1.0  # Zoom 80%
    driver.execute_script(f"document.body.style.zoom='{zoom_level}'")

    # Kiểm tra và tạo thư mục lưu ảnh chụp màn hình nếu chưa có
    screenshots_dir = 'screenshots'
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)

    return driver

def reload_website(driver, url, zoom_level=1.0):
    """
    Tải lại trang web và thiết lập lại tỷ lệ zoom.
    Args:
        driver (WebDriver): Đối tượng WebDriver đã khởi tạo.
        url (str): Địa chỉ URL của trang web cần tải lại.
        zoom_level (float, optional): Tỷ lệ zoom của trang web. Mặc định là 100%.
    """
    driver.get(url)
    driver.execute_script(f"document.body.style.zoom='{zoom_level}'")

def check_and_close_notifications(driver, xpath):
    """
    Kiểm tra sự tồn tại của phần tử với XPath và đóng thông báo nếu có.
    Args:
        driver (WebDriver): Đối tượng WebDriver đã khởi tạo.
        xpath (str): XPath của phần tử cần kiểm tra.
    """
    try:
        # Kiểm tra sự tồn tại của phần tử với XPath
        elements_to_check = driver.find_elements(By.XPATH, xpath)
        if elements_to_check:
            # Tắt tác vụ thông báo
            driver.execute_script("arguments[0].click();", elements_to_check[0])
            #print("Tắt thông báo trang Web")
    except Exception as e:
        print(f"Đã xảy ra lỗi khi kiểm tra và đóng thông báo: {e}")

def check_and_close_end_notifications(driver, xpath, invoice_data):
    # Kiểm tra sự tồn tại của phần tử với XPath
    time.sleep(1)
    expected_texts = ["thông tin tổ chức, cá nhân tìm kiếm"]
    elements_to_check = driver.find_elements(By.XPATH, xpath)
    #print(f"Đã tìm thấy {len(elements_to_check)} phần tử với XPath '{xpath}'")
    if elements_to_check:
        for element in elements_to_check:
            element_text = element.text
                #print(f"Giá trị văn bản của phần tử: '{element_text}'")
            if any(expected_text in element_text for expected_text in expected_texts):
                # Chụp màn hình và lưu lại với tên tệp là giá trị của SHDon
                screenshot_filename = os.path.join('screenshots', f"HD_{invoice_data['shdon']}.png")
                take_screenshot(driver, screenshot_path=screenshot_filename)
    else:
            print("Không tìm thấy phần tử với XPath cung cấp.\n") 
    
def get_invoice_data(data):
    """
    Lấy các giá trị cần thiết từ dữ liệu đầu vào.
    Args:
        data (dict): Dữ liệu đầu vào chứa các thông tin cần thiết.
    Returns:
        dict: Một từ điển chứa các giá trị được lấy ra.
    """
    return {
        'mst_nban': data.get('NBan_MST', ''),
        'khhdon': data.get('KHHDon', ''),
        'shdon': data.get('SHDon', ''),
        'tgtthue': data.get('TgTThue', ''),
        'tgtttbso': data.get('TgTTTBSo', '')
    }

def fill_invoice_data_hdgtgt(driver, invoice_data, config):
    """
    Điền các dữ liệu hóa đơn vào các trường tương ứng trên trang web.
    Args:
        driver (WebDriver): Đối tượng WebDriver đã khởi tạo.
        invoice_data (dict): Dữ liệu hóa đơn được lấy từ module `get_invoice_data`.
        config (ConfigParser): Đối tượng ConfigParser để lấy các giá trị XPath từ file config.ini.
    """
    # Loại bỏ phần đuôi .0000 hoặc .000000 nếu có
    if invoice_data['tgtthue'].endswith('.0000'):
        invoice_data['tgtthue'] = invoice_data['tgtthue'][:-5]  # Loại bỏ 5 ký tự cuối cùng ('.0000')
    elif invoice_data['tgtthue'].endswith('.000000'):
        invoice_data['tgtthue'] = invoice_data['tgtthue'][:-7]  # Loại bỏ 7 ký tự cuối cùng ('.000000')

    if invoice_data['tgtttbso'].endswith('.0000'):
        invoice_data['tgtttbso'] = invoice_data['tgtttbso'][:-5]  # Loại bỏ 5 ký tự cuối cùng ('.0000')
    elif invoice_data['tgtttbso'].endswith('.000000'):
        invoice_data['tgtttbso'] = invoice_data['tgtttbso'][:-7]  # Loại bỏ 7 ký tự cuối cùng ('.000000')

    # Điền dữ liệu vào các trường tương ứng
    driver.find_element(By.XPATH, input_MST_NBan).send_keys(invoice_data['mst_nban'])
    driver.find_element(By.XPATH, input_KHHDon).send_keys(invoice_data['khhdon'])
    driver.find_element(By.XPATH, input_SHDon).send_keys(invoice_data['shdon'])
    driver.find_element(By.XPATH, input_TgTThue).send_keys(invoice_data['tgtthue'])
    driver.find_element(By.XPATH, input_TgTTTBSo).send_keys(invoice_data['tgtttbso'])

def fill_invoice_data_hdbh(driver, invoice_data, config):
    """
    Điền các dữ liệu hóa đơn vào các trường tương ứng trên trang web.
    Args:
        driver (WebDriver): Đối tượng WebDriver đã khởi tạo.
        invoice_data (dict): Dữ liệu hóa đơn được lấy từ module `get_invoice_data`.
        config (ConfigParser): Đối tượng ConfigParser để lấy các giá trị XPath từ file config.ini.
    """
    # Loại bỏ phần đuôi .0000 hoặc .000000 nếu có
    if invoice_data['tgtthue'].endswith('.0000'):
        invoice_data['tgtthue'] = invoice_data['tgtthue'][:-5]  # Loại bỏ 5 ký tự cuối cùng ('.0000')
    elif invoice_data['tgtthue'].endswith('.000000'):
        invoice_data['tgtthue'] = invoice_data['tgtthue'][:-7]  # Loại bỏ 7 ký tự cuối cùng ('.000000')

    if invoice_data['tgtttbso'].endswith('.0000'):
        invoice_data['tgtttbso'] = invoice_data['tgtttbso'][:-5]  # Loại bỏ 5 ký tự cuối cùng ('.0000')
    elif invoice_data['tgtttbso'].endswith('.000000'):
        invoice_data['tgtttbso'] = invoice_data['tgtttbso'][:-7]  # Loại bỏ 7 ký tự cuối cùng ('.000000')

    
    # Điền dữ liệu vào các trường tương ứng
    driver.find_element(By.XPATH, select_LHDon_xpath).click()
    driver.find_element(By.XPATH, select_LHDonBH_xpath).click()
    driver.find_element(By.XPATH, input_MST_NBan).send_keys(invoice_data['mst_nban'])


    driver.find_element(By.XPATH, input_KHHDon).send_keys(invoice_data['khhdon'])
    driver.find_element(By.XPATH, input_SHDon).send_keys(invoice_data['shdon'])
    driver.find_element(By.XPATH, input_TgTThue).send_keys(invoice_data['tgtthue'])
    driver.find_element(By.XPATH, input_TgTTTBSo).send_keys(invoice_data['tgtttbso'])


def auto_fill_website_hdgtgt(data_list):
    # Khởi tạo trình duyệt và mở trang web
    driver = open_website()

    for data in data_list:

        reload_website(driver, url)
        # Kiểm tra sự tồn tại của phần tử với XPath
        check_and_close_notifications(driver, news_close_xpath)
        # Lấy dữ liệu hóa đơn và điền vào các trường
        invoice_data = get_invoice_data(data)
        fill_invoice_data_hdgtgt(driver, invoice_data, config)
        # Xử lý captcha
        time.sleep(1.5)
        captcha_browser(driver, input_captcha, button_click)
        # Kiểm tra kết quả 
        check_and_close_end_notifications(driver, tbketqua_xpath, invoice_data)
        # Tùy thuộc vào logic, bạn có thể cần thêm các bước khác như nhấp nút gửi, chờ đợi, v.v.
        time.sleep(0.5)  # Đợi 1 giây trước khi xử lý tệp tiếp theo
        #clear_screen()

def auto_fill_website_hdbh(data_list):
    # Khởi tạo trình duyệt và mở trang web
    driver = open_website()

    for data in data_list:

        reload_website(driver, url)
        # Kiểm tra sự tồn tại của phần tử với XPath
        check_and_close_notifications(driver, news_close_xpath)
        # Lấy dữ liệu hóa đơn và điền vào các trường
        invoice_data = get_invoice_data(data)
        fill_invoice_data_hdbh(driver, invoice_data, config)
        # Xử lý captcha
        time.sleep(1.5)
        captcha_browser(driver, input_captcha, button_click)
        # Kiểm tra kết quả 
        check_and_close_end_notifications(driver, tbketqua_xpath, invoice_data)
        # Tùy thuộc vào logic, bạn có thể cần thêm các bước khác như nhấp nút gửi, chờ đợi, v.v.
        time.sleep(0.5)  # Đợi 1 giây trước khi xử lý tệp tiếp theo
        #clear_screen()


def captcha_browser(driver, input_captcha_xpath, button_click_xpath):
    # Điền thông tin cần tra cứu hoá đơn
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    images = soup.find_all('img', src=lambda x: x and x.startswith('data:image/svg+xml;base64'))
    
    # In ra các liên kết
    for img in images:
        data_url = img['src']
        #print(data_url)
        
        # Kiểm tra và loại bỏ tiền tố 'data:image/svg+xml;base64,' nếu có
        if data_url.startswith("data:image/svg+xml;base64,"):
            data_url = data_url.split(",")[1]

        # Giải mã base64
        try:
            svg_data = base64.b64decode(data_url)
            #print("Giải mã base64 thành công")
        except base64.binascii.Error as e:
            print("Lỗi giải mã base64:", e)
            continue

        # Lưu nội dung SVG vào tệp
        with open("output.svg", "wb") as f:
            f.write(svg_data) 

        # In nội dung SVG ra màn hình
        #print("Nội dung SVG:")
        svg_captcha = svg_data.decode("utf-8")
        t = solver.solve_captcha(svg_captcha)
        
        # Nhập captcha và nhấn nút
        driver.find_element(By.XPATH, input_captcha_xpath).send_keys(t)
        driver.find_element(By.XPATH, button_click_xpath).click()

def take_screenshot(driver, screenshot_path='screenshot.png'):
    time.sleep(0)  # Điều chỉnh thời gian chờ nếu cần

    # Chụp toàn màn hình
    driver.save_screenshot(screenshot_path)
    # Mở ảnh chụp màn hình bằng Pillow
    image = Image.open(screenshot_path)
    
    # Tạo đối tượng ImageDraw để vẽ lên ảnh
    draw = ImageDraw.Draw(image)
    
    # Đường dẫn tới font chữ và kích thước font (bạn có thể thay đổi đường dẫn và kích thước)
    font_path = "arial.ttf"  # Thay đổi nếu cần
    font_size = 36  # Tăng kích thước font chữ
    font = ImageFont.truetype(font_path, font_size)
    
    # Tạo chuỗi text với ngày tháng năm hiện tại
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    text = f"{current_time}"
     # Sử dụng `textbbox` để xác định kích thước của văn bản
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Xác định vị trí để vẽ text (ở góc dưới bên phải)
    text_position = (10, image.height - 10 - text_height)
    
    # Vẽ text lên hình ảnh
    draw.text(text_position, text, font=font, fill=(0, 0, 0))  # Màu trắng
    
    # Lưu lại hình ảnh với text đã thêm
    image.save(screenshot_path)
    print(f">>Ảnh được lưu vào thư mục {screenshot_path}")

    # Mở ảnh chụp màn hình bằng Pillow và lưu lại nếu cần
    #image = Image.open(screenshot_path)
    #image.show()
