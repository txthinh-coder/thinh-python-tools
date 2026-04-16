import base64
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import configparser
from solvers.svgcaptcha import solver

# Đọc file config.ini
config = configparser.ConfigParser()
config.read('config.ini')

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

driver = webdriver.Chrome()
driver.maximize_window()

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


driver.get(url)
elements = driver.find_elements(By.XPATH, news_close_xpath)
if elements:
    elements[0].click()

driver.find_element(By.XPATH, input_MST_NBan).send_keys('mst_nban')
driver.find_element(By.XPATH, input_KHHDon).send_keys('1')
driver.find_element(By.XPATH, input_SHDon).send_keys('1')
driver.find_element(By.XPATH, input_TgTThue).send_keys('tgtthue')
driver.find_element(By.XPATH, input_TgTTTBSo).send_keys('tgtttbso')
captcha_browser(driver, input_captcha, button_click)
time.sleep(5)
row_data = driver.find_element(By.XPATH, tbketqua_xpath)
print("Row 1: ", row_data.text)