from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import os
import re

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


# ฟังก์ชันที่ใช้ในการอ่านไฟล์ภาพจาก 2 โฟลเดอร์และบันทึกลง PostgreSQL
def process_images(cam01_folder, cam02_folder, **kwargs):
    # สร้าง connection ไปยัง PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    
    # อ่านไฟล์ภาพจากทั้งสองโฟลเดอร์
    cam01_images = sorted(os.listdir(cam01_folder))  # เรียงตามชื่อไฟล์
    cam02_images = sorted(os.listdir(cam02_folder))  # เรียงตามชื่อไฟล์
    
    # ตรวจสอบว่าจำนวนไฟล์ใน cam01 และ cam02 ตรงกัน
    if len(cam01_images) != len(cam02_images):
        raise ValueError("จำนวนไฟล์ใน cam01 และ cam02 ไม่ตรงกัน")
    
    # สำหรับแต่ละไฟล์ใน cam01 และ cam02
    for cam01_image, cam02_image in zip(cam01_images, cam02_images):
        if cam01_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')) and \
           cam02_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            try:
                # ดึง timestamp จากชื่อไฟล์ใน cam01
                timestamp = extract_timestamp_from_filename(cam01_image)
                
                # เก็บที่อยู่ของไฟล์จาก cam01 และ cam02
                file_path_1 = os.path.join(cam01_folder, cam01_image)
                file_path_2 = os.path.join(cam02_folder, cam02_image)
                status = 'incomplete'
                count_bbox = 0
                
                # SQL สำหรับการ insert ข้อมูลลงใน PostgreSQL
                insert_query = """
                INSERT INTO cameras_images (timestamp, status, file_path_1, file_path_2, count_bbox)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                # รันคำสั่ง insert
                pg_hook.run(insert_query, parameters=(timestamp, status, file_path_1, file_path_2, count_bbox))
                
                # ปริ้นข้อความเมื่อบันทึกสำเร็จ
                print(f"บันทึกสำเร็จ: {file_path_1}, {file_path_2}")
            
            except ValueError as e:
                # ถ้าไฟล์มีรูปแบบชื่อที่ไม่ถูกต้อง จะข้ามไฟล์นี้ไป
                print(e)

# ฟังก์ชันที่ใช้ในการ query ข้อมูลจาก PostgreSQL
def query_saved_images(**kwargs):
    # สร้าง connection ไปยัง PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    
    # SQL สำหรับการ query ข้อมูล
    query = "SELECT * FROM cameras_images"
    
    # รันคำสั่ง query และดึงข้อมูล
    results = pg_hook.get_records(query)
    
    # แสดงผลลัพธ์ที่ได้
    for record in results:
        print(record)

# กำหนด default arguments ของ DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
}

# กำหนด DAG
with DAG(dag_id='process_image_files',
         default_args=default_args,
         schedule_interval='@daily',  # รันทุกวัน
         catchup=False) as dag:
    
    # Task สำหรับการประมวลผลไฟล์ภาพ
    process_images_task = PythonOperator(
    task_id='process_images',
    python_callable=process_images,
    op_kwargs={'cam01_folder': '/usr/local/spark/assets/cam01',
               'cam02_folder': '/usr/local/spark/assets/cam02'},
    provide_context=True
)

    # Task สำหรับการ query ข้อมูล
    query_images_task = PythonOperator(
        task_id='query_saved_images',
        python_callable=query_saved_images,
        provide_context=True
    )

    # กำหนดลำดับของ Task
    process_images_task >> query_images_task