import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime, timedelta

###############################################
# Parameters
###############################################
spark_conn = os.environ.get("spark_default", "spark_default")
spark_master = "spark://spark:7077"

image_output_dir = "../../images"

###############################################
# DAG Definition
###############################################
now = datetime.now()

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(now.year, now.month, now.day),
    "email": ["airflow@airflow.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG(
    dag_id="save-images-job",
    description="This DAG triggers a Spark job to download images from URLs and save them to a specified directory.",
    default_args=default_args,
    schedule_interval=timedelta(1)  # Run daily
)

start = DummyOperator(task_id="start", dag=dag)

spark_job_save_images = SparkSubmitOperator(
    task_id="spark_job_save_images",
    application="/usr/local/spark/applications/save_image.py",
    name="save-images",
    conn_id=spark_conn,
    verbose=1,
    conf={"spark.master": spark_master},
    application_args=[image_output_dir],  # ส่ง args ให้กับ save_image.py
    dag=dag)

end = DummyOperator(task_id="end", dag=dag)

start >> spark_job_save_images >> end
