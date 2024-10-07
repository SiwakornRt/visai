from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
from datetime import datetime

# ฟังก์ชันสำหรับ query ข้อมูลจาก PostgreSQL และบันทึกเป็นไฟล์ CSV
def query_and_save_as_csv(**kwargs):
    # สร้าง connection ไปยัง PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_connection')
    
    # SQL สำหรับการ query ข้อมูลจากตาราง cameras_images
    query = "SELECT * FROM cameras_images"
    
    # รันคำสั่ง query และดึงข้อมูลเป็น DataFrame โดยใช้ Pandas
    connection = pg_hook.get_conn()
    df = pd.read_sql(query, connection)
    
    # เซฟข้อมูลเป็นไฟล์ CSV
    csv_file_path = '/usr/local/spark/assets/data/cameras_images_data2.csv'  # ระบุ path ที่ต้องการเซฟ
    df.to_csv(csv_file_path, index=False)
    
    print(f"Data saved to {csv_file_path}")

# กำหนด default arguments ของ DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
}

# กำหนด DAG
with DAG(dag_id='query_and_save_csv',
         default_args=default_args,
         schedule_interval='@daily',  # รันทุกวัน
         catchup=False) as dag:
    
    # Task สำหรับการ query ข้อมูลและบันทึกเป็นไฟล์ CSV
    query_and_save_task = PythonOperator(
        task_id='query_and_save_as_csv',
        python_callable=query_and_save_as_csv,
        provide_context=True
    )
