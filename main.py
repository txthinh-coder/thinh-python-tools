import configparser
import os
import printer_folder
from xml_processor import process_directory_to_excel, get_all_data_from_directory
from auto_fill_website import auto_fill_website_hdbh, auto_fill_website_hdgtgt
from excel_processor import process_excel_data
from auto_update_chromedriver import update_chromedriver_if_needed, get_chrome_version, get_current_chromedriver_version
from selenium import webdriver
from printer_folder import print_all_images_in_folder
# Đặt đường dẫn thư mục chứa hình và tên máy in
folder_path = os.path.join(os.getcwd(), "screenshots")  # Thay bằng thư mục chứa hình
# Đọc file config.ini với mã hóa UTF-8
config = configparser.ConfigParser() 
with open('config.ini', 'r', encoding='utf-8') as configfile:
    config.read_file(configfile)
url = config.get('settings', 'url')
excel_path = config.get('settings','excel_path')


def clear_screen():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux, Mac
        os.system('clear')

def print_bidv_logo():
    logo = r"""
██████      ██     ██████      ██    ██     ███████  █████  ██      ██████   ██████  ███    ██ 
██   ██     ██     ██   ██     ██    ██     ██      ██   ██ ██     ██       ██    ██ ████   ██ 
██████      ██     ██   ██     ██    ██     ███████ ███████ ██     ██   ███ ██    ██ ██ ██  ██ 
██   ██     ██     ██   ██      ██  ██           ██ ██   ██ ██     ██    ██ ██    ██ ██  ██ ██ 
██████      ██     ██████        ████       ███████ ██   ██ ██      ██████   ██████  ██   ████  
"""
    print(logo)



def main():
    while True:
        clear_screen()
        """Kiểm tra phiên bản ChromeDriver và xử lý tùy chọn cập nhật nếu cần"""
        chrome_version = get_chrome_version()
        chromedriver_version = get_current_chromedriver_version()

        # In ra console
        print(f"🟢 Phiên bản Chrome: {chrome_version}")
        print(f"🟢 Phiên bản ChromeDriver: {chromedriver_version}")
        if chromedriver_version != chrome_version:
            print("\n⚠️ Phiên bản ChromeDriver không tương thích với Chrome!")
            print("Bạn có muốn cập nhật ChromeDriver không?")
            print("1. Có, cập nhật ngay")
            print("2. Bỏ qua, chạy tiếp (có thể bị lỗi)")
            print("3. Thoát")
            choice = input("Nhập số tương ứng với lựa chọn: ").strip()
            if choice == "1":
                update_chromedriver_if_needed()
            elif choice == "3":
                print("🚪 Thoát chương trình!")
                return
        
        # Khởi chạy trình duyệt sau khi kiểm tra hoặc cập nhật xong
        #driver = webdriver.Chrome()
        #chrome_version = driver.capabilities['browserVersion']
        #chromedriver_version = driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]

        #print(f"🟢 Phiên bản Chrome: {chrome_version}")
        #print(f"🟢 Phiên bản ChromeDriver: {chromedriver_version}")

        # Đóng trình duyệt
        #driver.quit()
        #print_bidv_logo()
        #print('Tác giả thiết kế lên ý tưởng: thầy ông nội')
        print("Link: ", url)
        #print("Tool: Tự động tra cứu & xuất dữ liệu hoá đơn")
        print("Chọn lựa chọn:")
        print("1. Tra cứu Hóa đơn giá trị gia tăng từ file XML")
        print("2. Tra cứu Hóa đơn bán hàng từ file XML")
        print("3. Tra cứu từ file excel",excel_path)
        print("4. Xuất dữ liệu file .XML sang file Excel")
        print("5. In file hoá đơn trong thư mục screenshots")
        print("6. Thoát")

        choice = input("Nhập số tương ứng với tùy chọn: ").strip()

        if choice == '1':
            # Lấy đường dẫn thư mục từ file config.ini
            directory = config['settings']['hddt_gtgt_xml_directory']
            
            # Kiểm tra xem có file .xml nào trong thư mục không
            xml_files = [f for f in os.listdir(directory) if f.endswith('.xml')]
            
            if not xml_files:
                print("Không có file .xml nào trong thư mục.")
            else:
                # Lấy danh sách dữ liệu từ các tệp XML
                data_list = get_all_data_from_directory(directory)
                
                # Tự động điền dữ liệu vào website
                auto_fill_website_hdgtgt(data_list)
            input("Nhấn Enter để quay lại menu...")  # Dừng màn hình cho người dùng xem kết quả    
            clear_screen()    
        
        elif choice == '2':
            # Lấy đường dẫn thư mục từ file config.ini
            directory = config['settings']['hddt_hdbh_xml_directory']
            
            # Kiểm tra xem có file .xml nào trong thư mục không
            xml_files = [f for f in os.listdir(directory) if f.endswith('.xml')]
            
            if not xml_files:
                print("Không có file .xml nào trong thư mục.")
            else:
                # Lấy danh sách dữ liệu từ các tệp XML
                data_list = get_all_data_from_directory(directory)
                
                # Tự động điền dữ liệu vào website
                auto_fill_website_hdbh(data_list)
            input("Nhấn Enter để quay lại menu...")  # Dừng màn hình cho người dùng xem kết quả    
            clear_screen()    
        
        elif choice == '3':     
            # Tự động điền dữ liệu vào website
            process_excel_data()
            input("Nhấn Enter để quay lại menu...")  # Dừng màn hình cho người dùng xem kết quả
            clear_screen()

        elif choice == '4':
            # Lấy đường dẫn thư mục từ file config.ini
            directory = config['settings']['hddt_gtgt_xml_directory']
            xml_files = [f for f in os.listdir(directory) if f.endswith('.xml')]
            
            if not xml_files:
                print("Không có file .xml nào trong thư mục.")
            else:
                output_file = 'output_report_XML.xlsx'
                process_directory_to_excel(directory, output_file)
                print(f"Dữ liệu đã được xử lý và lưu vào {output_file}.")
            input("Nhấn Enter để quay lại menu...")  # Dừng màn hình cho người dùng xem kết quả
            clear_screen()    

        elif choice == '5':
            print("In file screenshots.")
            # Gọi hàm in mà không cần chỉ định máy in (dùng mặc định)
            printer_folder.print_all_images_in_folder(folder_path)
            clear_screen()
        
        elif choice == '6':
            print("Thoát chương trình.")
            break

        else:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            input("Nhấn Enter để quay lại menu...")  # Dừng màn hình cho người dùng xem kết quả
            clear_screen()

if __name__ == '__main__':
    main()