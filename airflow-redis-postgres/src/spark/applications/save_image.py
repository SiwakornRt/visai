import sys
import requests  # สำหรับดาวน์โหลดไฟล์รูปจาก URL
import os  # สำหรับการจัดการ directory
from datetime import datetime  # สำหรับการตั้งชื่อไฟล์ด้วย timestamp

####################################
# Parameters
####################################
image_output_dir = sys.argv[1]  # พารามิเตอร์สำหรับ directory ที่จะเก็บรูปภาพ

# สร้าง directory ถ้ายังไม่มี
if not os.path.exists(image_output_dir):
    os.makedirs(image_output_dir)

####################################
# Download images and save to directory
####################################
print("######################################")
print("DOWNLOADING IMAGES")
print("######################################")

def download_image(image_url, output_dir):
    try:
        # สร้างชื่อไฟล์จาก timestamp ปัจจุบัน
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = image_url.split('.')[-1]  # ดึงนามสกุลไฟล์จาก URL เช่น jpg, png
        file_name = f"{timestamp}.{file_extension}"
        file_path = os.path.join(output_dir, file_name)
        
        # ดาวน์โหลดรูปภาพ
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded image: {file_path}")
        else:
            print(f"Failed to download image: {image_url}")
    except Exception as e:
        print(f"Error downloading image: {e}")

# ตัวอย่าง image URLs ที่จะดาวน์โหลด
image_urls = [
    "http://172.30.9.138/ISAPI/Streaming/channels/101/picture",
    # เพิ่ม URL รูปภาพอื่น ๆ ที่ต้องการดาวน์โหลด
]

for image_url in image_urls:
    download_image(image_url, image_output_dir)
