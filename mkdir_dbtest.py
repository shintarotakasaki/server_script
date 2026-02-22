import subprocess
import datetime
import sqlite3
import os
import time
from google.cloud import storage
import sqlite_practice


def get_gpu_temp():
    try:
        # nvidia-smiから温度を取得
        cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        temp = subprocess.check_output(cmd.split()).decode('utf-8').strip()
        return temp
    except Exception as e:
        print(f"GPUtemp get as false...: {e}")
        return "99" # テスト用ダミー

def upload_to_gcs(db_path):

    BUCKET_NAME = 'linux-server-1'
    try:
        # 環境変数から認証情報を読み込み
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        filename = f'gpu_logs/{os.path.basename(db_path)}'

        blob = bucket.blob(filename)
        blob.upload_from_filename(db_path)

        #print(f"success!://{BUCKET_NAME}/{filename}")
    except Exception as e:
        print(f"false...: {e}")

def daily_summary_db(path):
    conn = sqlite3.connect(path)
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
    #start_time = time.time()

    while True:
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        dir_path = "/home/admin-user/server_script/Server_log_dir"
        db_path = f"/home/admin-user/server_script/Server_log_dir/test_summary{today_str}.db"
        daily_summary_db(db_path)

        if not os.path.exists(db_path):
            yesterday = today_str - datetime.timedelta(days=1)
            yesterday_db = f"{dir_path}/test_summary_{yesterday.strftime('%Y-%m-%d')}.db"
            if os.path.exists(yesterday_db):
                upload_to_gcs(yesterday_db)

            # ② 7日前の日付を計算して、サーバーから削除！（容量節約）
            seven_days_ago = today_str - datetime.timedelta(days=7)
            old_db = f"{dir_path}/test_summary_{seven_days_ago.strftime('%Y-%m-%d')}.db"
            if os.path.exists(old_db):
                os.remove(old_db)
            
            upload_to_gcs(db_path)
        databace = sqlite_practice.test_DB()
        summary = sqlite_practice.summary_output(databace)
        #print(f"タプル{summary}")


        insert_data = summary + (now_str,)

        disk_conn = sqlite3.connect(db_path)
        disk_cursor = disk_conn.cursor()

        disk_cursor.execute('''
            INSERT INTO daily_summary
            (
                CPU_temp, CPU_per,
                GPU_temp, GPU_per,
                RAM_temp, RAM_per,
                SSD_temp, LAN_temp,
                timestamp
            ) VALUES(?,?,?,?,?,?,?,?,?)
        ''', insert_data)

        disk_conn.commit()
        disk_conn.close()

        #end_time = time.time()
        #syorizikan = end_time - start_time
        #print(f"処理時間：{syorizikan:.6f}秒")

