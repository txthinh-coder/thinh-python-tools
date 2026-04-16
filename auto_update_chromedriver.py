import os
import zipfile
import requests
import shutil
import subprocess
import re

# 📌 Đường dẫn tới ChromeDriver
CHROMEDRIVER_PATH = "./chromedriver.exe"

def get_chrome_version():
    """Lấy phiên bản Chrome đang cài đặt"""
    try:
        output = subprocess.check_output(
            r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" get Version /value',
            shell=True
        ).decode().strip()
        version = re.search(r"Version=(\d+\.\d+\.\d+\.\d+)", output)
        return version.group(1) if version else None
    except Exception:
        return None

def get_current_chromedriver_version():
    """Lấy phiên bản ChromeDriver hiện tại"""
    try:
        output = subprocess.check_output([CHROMEDRIVER_PATH, "--version"], stderr=subprocess.DEVNULL).decode().strip()
        version = re.search(r"ChromeDriver (\d+\.\d+\.\d+\.\d+)", output)
        return version.group(1) if version else None
    except Exception:
        return None  # Nếu không tìm thấy phiên bản, trả về None

def get_chromedriver_download_url(chrome_version):
    """Tạo URL tải ChromeDriver tương ứng"""
    return f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/win64/chromedriver-win64.zip"

def remove_old_chromedriver():
    """Xóa ChromeDriver cũ"""
    if os.path.exists(CHROMEDRIVER_PATH):
        os.remove(CHROMEDRIVER_PATH)
        print("✅ Đã xóa ChromeDriver cũ!")

def download_and_extract_chromedriver(url):
    """Tải và giải nén ChromeDriver mới"""
    try:
        # Lấy thư mục chứa ChromeDriver từ đường dẫn file
        chromedriver_dir = os.path.dirname(os.path.abspath(CHROMEDRIVER_PATH))

        zip_path = os.path.join(chromedriver_dir, "chromedriver.zip")

        print(f"📥 Đang tải từ: {url}")
        response = requests.get(url, stream=True)
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print("📂 Giải nén ChromeDriver vào:", chromedriver_dir)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(chromedriver_dir)

        os.remove(zip_path)

        # Di chuyển chromedriver.exe từ thư mục giải nén vào đúng vị trí
        extracted_path = os.path.join(chromedriver_dir, "chromedriver-win64", "chromedriver.exe")
        shutil.move(extracted_path, CHROMEDRIVER_PATH)

        # Xóa thư mục tạm sau khi di chuyển xong
        shutil.rmtree(os.path.join(chromedriver_dir, "chromedriver-win64"))

        print("✅ Cập nhật ChromeDriver thành công!")
        chrome_version = get_chrome_version()
        chromedriver_version = get_current_chromedriver_version()

        # In ra console
        print(f"🟢 Phiên bản Chrome: {chrome_version}")
        print(f"🟢 Phiên bản ChromeDriver: {chromedriver_version}")
    except Exception as e:
        print("❌ Lỗi khi tải hoặc giải nén:", e)

def update_chromedriver_if_needed():
    """Tự động cập nhật ChromeDriver nếu cần"""
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("❌ Không tìm thấy Chrome! Hãy kiểm tra lại cài đặt.")
        return False

    chromedriver_version = get_current_chromedriver_version()
    print(f"🔍 Chrome: {chrome_version}, ChromeDriver: {chromedriver_version}")

    if chromedriver_version != chrome_version:
        print("⚠️ Phiên bản không khớp! Đang cập nhật ChromeDriver...")
        remove_old_chromedriver()
        url = get_chromedriver_download_url(chrome_version)
        download_and_extract_chromedriver(url)
        return True  # Đã cập nhật
    else:
        print("✅ ChromeDriver đã khớp phiên bản với Chrome!")
        return False  # Không cần cập nhật