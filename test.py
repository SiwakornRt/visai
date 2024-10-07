import re
from datetime import datetime
# ฟังก์ชันที่ใช้ในการดึง timestamp จากชื่อไฟล์
def extract_timestamp_from_filename(filename):
    # ใช้ regular expression เพื่อดึงข้อมูล timestamp จากชื่อไฟล์ในรูปแบบ cam_1YYYYMMDD_HHMMSS
    match = re.match(r'cam_1(\d{8})_(\d{6})', filename)
    if match:
        date_str = match.group(1)  # YYYYMMDD
        time_str = match.group(2)  # HHMMSS
        
        # แปลงจาก string ไปเป็น datetime object
        timestamp = datetime.strptime(f'{date_str} {time_str}', '%Y%m%d %H%M%S')
        return timestamp
    else:
        raise ValueError(f"Invalid filename format: {filename}")

filename = 'cam_120241004_131045.jpg'
timestamp = extract_timestamp_from_filename(filename)
print(timestamp)  # Output: 2024-10-04 13:10:45