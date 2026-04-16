import os
import xml.etree.ElementTree as ET
import pandas as pd

def parse_xml_to_dict(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    data = {}
    
    def get_element_text(element, tag):
        child = element.find(tag)
        return child.text if child is not None else ''
    
    # TTChung
    ttchung = root.find('.//TTChung')
    if ttchung is not None:
        data.update({
            "PBan": get_element_text(ttchung, 'PBan'),
            "THDon": get_element_text(ttchung, 'THDon'),
            "KHMSHDon": get_element_text(ttchung, 'KHMSHDon'),
            "KHHDon": get_element_text(ttchung, 'KHHDon'),
            "SHDon": get_element_text(ttchung, 'SHDon'),
            "NLap": get_element_text(ttchung, 'NLap'),
            "SBKe": get_element_text(ttchung, 'SBKe'),
            "NBKe": get_element_text(ttchung, 'NBKe'),
            "DVTTe": get_element_text(ttchung, 'DVTTe'),
            "TGia": get_element_text(ttchung, 'TGia'),
            "HTTToan": get_element_text(ttchung, 'HTTToan'),
            "MSTTCGP": get_element_text(ttchung, 'MSTTCGP')
        })
    
    # NDHDon/NBan
    nban = root.find('.//NBan')
    if nban is not None:
        data.update({
            "NBan_Ten": get_element_text(nban, 'Ten'),
            "NBan_MST": get_element_text(nban, 'MST'),
            "NBan_DChi": get_element_text(nban, 'DChi')
        })
        
    # NDHDon/NMua
    nmua = root.find('.//NMua')
    if nmua is not None:
        data.update({
            "NMua_Ten": get_element_text(nmua, 'Ten'),
            "NMua_MST": get_element_text(nmua, 'MST'),
            "NMua_DChi": get_element_text(nmua, 'DChi'),
            "NMua_MKHang": get_element_text(nmua, 'MKHang'),
            "NMua_SDThoai": get_element_text(nmua, 'SDThoai'),
            "NMua_HVTNMHang": get_element_text(nmua, 'HVTNMHang')
        })
        
    # DSHHDVu/HHDVu
    dshhdvu = root.find('.//DSHHDVu')
    if dshhdvu is not None:
        for idx, hhdvu in enumerate(dshhdvu.findall('HHDVu')):
            data.update({
                f"HHDVu_{idx+1}_TChat": get_element_text(hhdvu, 'TChat'),
                f"HHDVu_{idx+1}_STT": get_element_text(hhdvu, 'STT'),
                f"HHDVu_{idx+1}_THHDVu": get_element_text(hhdvu, 'THHDVu'),
                f"HHDVu_{idx+1}_TLCKhau": get_element_text(hhdvu, 'TLCKhau'),
                f"HHDVu_{idx+1}_STCKhau": get_element_text(hhdvu, 'STCKhau'),
                f"HHDVu_{idx+1}_ThTien": get_element_text(hhdvu, 'ThTien'),
                f"HHDVu_{idx+1}_TSuat": get_element_text(hhdvu, 'TSuat')
            })
    
    # TToan
    ttoan = root.find('.//TToan')
    if ttoan is not None:
        ttsuat = ttoan.find('.//LTSuat')
        if ttsuat is not None:
            data.update({
                "LTSuat_TSuata": get_element_text(ttsuat, 'TSuat'),
                "LTSuat_ThTien": get_element_text(ttsuat, 'ThTien'),
                "LTSuat_TThue": get_element_text(ttsuat, 'TThue')
            })
        data.update({
            "TgTCThue": get_element_text(ttoan, 'TgTCThue'),
            "TgTThue": get_element_text(ttoan, 'TgTThue'),
            "TgTTTBSo": get_element_text(ttoan, 'TgTTTBSo'),
            "TgTTTBChu": get_element_text(ttoan, 'TgTTTBChu')
        })

    # Loại bỏ phần đuôi .0000 hoặc .000000 nếu có
    if data.get('TgTThue', '').endswith('.0000'):
        data['TgTThue'] = data['TgTThue'][:-5]
    elif data.get('TgTThue', '').endswith('.000000'):
        data['TgTThue'] = data['TgTThue'][:-7]
    
    if data.get('TgTTTBSo', '').endswith('.0000'):
        data['TgTTTBSo'] = data['TgTTTBSo'][:-5]
    elif data.get('TgTTTBSo', '').endswith('.000000'):
        data['TgTTTBSo'] = data['TgTTTBSo'][:-7]

    # TTKhac
    ttkhac = root.find('.//TTKhac')
    if ttkhac is not None:
        for ttin in ttkhac.findall('TTin'):
            ttruong = get_element_text(ttin, 'TTruong')
            dlieu = get_element_text(ttin, 'DLieu')
            data[f"TTKhac_{ttruong}"] = dlieu
    
    return data

def process_directory_to_excel(directory, output_file):
    files = sorted([f for f in os.listdir(directory) if f.endswith('.xml')])
    all_data = []
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        data = parse_xml_to_dict(file_path)
        all_data.append(data)
    
    df = pd.DataFrame(all_data)
    df.to_excel(output_file, index=False)

def get_all_data_from_directory(directory):
    files = sorted([f for f in os.listdir(directory) if f.endswith('.xml')])
    all_data = []
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        data = parse_xml_to_dict(file_path)
        all_data.append(data)
    
    return all_data