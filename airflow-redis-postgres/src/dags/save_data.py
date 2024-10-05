from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import os
import re

# ฟังก์ชันที่ใช้ในการดึง timestamp จากชื่อไฟล์
def extract_timestamp_from_filename(filename):
    # ใช้ regular expression เพื่อดึงข้อมูล timestamp จากชื่อไฟล์
    match = re.match(r'(\d{8})_(\d{6})', filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        
        # แปลงจาก string ไปเป็น datetime object
        timestamp = datetime.strptime(f'{date_str} {time_str}', '%Y%m%d %H%M%S')
        return timestamp
    else:
        raise ValueError(f"Invalid filename format: {filename}")

# ฟังก์ชันที่ใช้ในการอ่านไฟล์ภาพจากโฟลเดอร์และบันทึกลง PostgreSQL
def process_images(folder_path, **kwargs):
    # สร้าง connection ไปยัง PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    
    # อ่านไฟล์ภาพจากโฟลเดอร์
    images = os.listdir(folder_path)
    
    # สำหรับแต่ละไฟล์ในโฟลเดอร์
    for image in images:
        if image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
            try:
                # ดึง timestamp จากชื่อไฟล์
                timestamp = extract_timestamp_from_filename(image)
                
                # เก็บที่อยู่ของไฟล์และสถานะเป็น 'incomplete'
                file_path = os.path.join(folder_path, image)
                status = 'incomplete'
                
                # SQL สำหรับการ insert ข้อมูลลงใน PostgreSQL
                insert_query = """
                INSERT INTO cameras_images (timestamp, status, image_path)
                VALUES (%s, %s, %s)
                """
                
                # รันคำสั่ง insert
                pg_hook.run(insert_query, parameters=(timestamp, status, file_path))
                
                # ปริ้นข้อความเมื่อบันทึกสำเร็จ
                print(f"Save รูปสำเร็จ: {file_path}")
            
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
        op_kwargs={'folder_path': '/usr/local/spark/assets/data/images'},
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