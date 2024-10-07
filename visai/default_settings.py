APP_TITLE = "visai"

DEBUG = False

CACHE_REDIS_URL = "redis://localhost:6379"
REDIS_URL = "redis://localhost"
CACHE_TYPE = "SimpleCache"

SQLALCHEMY_DATABASE_URI = "sqlite:///project.db"
AIRFLOW_DATABASE_URI = "postgresql://airflow:airflow@postgres:5431/airflow"
VISAI_DATA = "data"
