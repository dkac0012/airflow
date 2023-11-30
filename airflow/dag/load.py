from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import requests
import json
import pendulum

# MySQL 연결 설정
mysql_host = ''
mysql_user = ''
mysql_password = ''
mysql_database = 'upbitbtc'
mysql_table = 'upbit_data'

# DAG 설정
default_args = {
    'owner': 'airflow', # 디폴트가 airflow이다.
    'depends_on_past': False,
    'email': ['dkac0012@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
    'start_date': pendulum.datetime(2023,11,8, tz="Asia/Seoul"),
}

dag = DAG('upbit_to_mysql_1', default_args=default_args, schedule_interval='9 1 * * *')

# Upbit API 호출 함수
def get_upbit_data():
    url = "https://api.upbit.com/v1/candles/days"
    querystring = {"market":"KRW-BTC","count":"2"}
    
    response = requests.request("GET", url, params=querystring)
    data = json.loads(response.text)
    data = data[0]
    return data


# MySQL 연결 생성 함수
def connect_to_mysql():
    import pymysql
    cnx = pymysql.connect(user=mysql_user, password=mysql_password,
                                  host=mysql_host, database=mysql_database)
    cursor = cnx.cursor()
    return cnx, cursor

# MySQL 데이터 적재 함수
def load_data_to_mysql(data):
    cnx, cursor = connect_to_mysql()
    sql = "INSERT INTO upbit_data (date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s)"
# 데이터 삽입
    
    index = data["candle_date_time_kst"].replace("T", " ")
    open = data["opening_price"]
    high = data["high_price"]
    low = data["low_price"]
    close = data["trade_price"]
    volume = data["candle_acc_trade_volume"]
    cursor.execute(sql, (index, open, high, low, close, volume))
    cnx.commit()
    cursor.close()
    cnx.close()

# Task 생성
t1 = PythonOperator(
    task_id='get_btc_data',
    python_callable=get_upbit_data,
    dag=dag
)

t3 = PythonOperator(
    task_id='load_btc_data_to_mysql',
    python_callable=load_data_to_mysql,
    dag=dag,
    op_kwargs={'data': t1.output}
)

t1 >> t3
