import subprocess
import datetime
import sqlite3
import os
from google.cloud import storage

# 【重要】ここを自分のバケット名に書き換えてください
BUCKET_NAME = 'linux-server-1'

def get_gpu_temp():
    try:
        # nvidia-smiから温度を取得
        cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        temp = subprocess.check_output(cmd.split()).decode('utf-8').strip()
        return temp
    except Exception as e:
        print(f"GPUtemp get as false...: {e}")
        return "99" # テスト用ダミー

def upload_to_gcs(text_data):
    try:
        # 環境変数から認証情報を読み込み
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'gpu_logs/temp_{now}.txt'

        blob = bucket.blob(filename)
        blob.upload_from_string(f"Temperature: {text_data}C")

        print(f"success!://{BUCKET_NAME}/{filename}")
    except Exception as e:
        print(f"false...: {e}")

def daily_summary_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            CPU_temp REAL, CPU_per REAL,
            GPU_temp REAL, GPU_per REAL,
            RAM_temp REAL, RAM_per REAL,
            SSD_temp REAL,
            LAN_temp REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn

if __name__ == "__main__":
    dir_path = "/home/admin-user/server_script/Server_log_dir"
    dir_dbpath = "/home/admin-user/server_script/Server_log_dir/test_summary.db"
    daily_summary_db(dir_dbpath)