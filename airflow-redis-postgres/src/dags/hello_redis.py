from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import redis

# ฟังก์ชันสำหรับการเชื่อมต่อ Redis และปริ้น Hello, World
def hello_world_redis():
    # เชื่อมต่อกับ Redis
    r = redis.Redis(host='redis', port=6379, db=0)

    # เก็บข้อความใน Redis
    r.set('greeting', 'Hello, Redis!')

    # ดึงข้อความจาก Redis
    greeting = r.get('greeting').decode('utf-8')
    
    # ปริ้นข้อความ
    print(greeting)

# ฟังก์ชันสำหรับการ Query ข้อมูลจาก PostgreSQL
def query_postgres():
    # สร้าง connection ไปยัง PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='my_postgres_connection')

    # SQL สำหรับการ Query ข้อมูลจาก Table cameras_images
    query = "SELECT * FROM cameras_images"

    # รันคำสั่ง query และดึงผลลัพธ์
    records = pg_hook.get_records(query)

    # ปริ้นผลลัพธ์ที่ดึงมา
    for record in records:
        print(record)

# กำหนด default arguments ของ DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 1),
    'retries': 1,
}

# กำหนด DAG
with DAG(dag_id='test_redis_and_postgres_dag',
         default_args=default_args,
         schedule_interval='@daily',  # รันทุกวัน
         catchup=False) as dag:

    # Task สำหรับการ Query ข้อมูลจาก PostgreSQL
    query_postgres_task = PythonOperator(
        task_id='query_postgres_task',
        python_callable=query_postgres
    )

    # Task สำหรับการปริ้น Hello, World
    hello_redis_task = PythonOperator(
        task_id='hello_world_task',
        python_callable=hello_world_redis
    )

    # ตั้งค่าให้ Task query_postgres_task รันก่อน hello_redis_task
    query_postgres_task >> hello_redis_task
