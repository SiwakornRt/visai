from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

# ฟังก์ชันที่ใช้ในการอัพเดต count_bbox ใน PostgreSQL
def update_count_bbox_from_file(file_path, **kwargs):
    # สร้าง connection ไปยัง PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    
    # อ่านไฟล์และอัพเดตข้อมูลในฐานข้อมูล
    with open(file_path, 'r') as file:
        print(file)
        for line in file:
            print('--------------------use--------------------')
            filename, count_bbox_str = line.strip().split(',')
            count_bbox = int(count_bbox_str)  # แปลงเป็น int
            
            # สร้าง query สำหรับอัพเดต count_bbox
            filename = f"/usr/local/spark/assets/cam01/{filename}"
            update_query = """
            UPDATE cameras_images 
            SET count_bbox = %s 
            WHERE file_path_1 = %s OR file_path_2 = %s
            """
            
            # รันคำสั่ง update
            pg_hook.run(update_query, parameters=(count_bbox, filename, filename))
            print(f"Updated {filename} with count_bbox: {count_bbox}")

# กำหนด default arguments ของ DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
}

# กำหนด DAG
with DAG(dag_id='update_count_bbox',
         default_args=default_args,
         schedule_interval='@daily',  # รันทุกวัน
         catchup=False) as dag:
    
    # Task สำหรับการอัพเดต count_bbox
    update_bbox_task = PythonOperator(
        task_id='update_count_bbox',
        python_callable=update_count_bbox_from_file,
        op_kwargs={'file_path': '/usr/local/spark/assets/data/bounding_boxes_count.txt'},  # ปรับที่อยู่ไฟล์ให้ถูกต้อง
        provide_context=True
    )
