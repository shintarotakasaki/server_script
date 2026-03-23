import subprocess
import datetime
import sqlite3
import os
import time
import csv
from google.cloud import storage
import dsql_pra


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
            GPU0_temp REAL, GPU0_per REAL,
            GPU1_temp REAL, GPU1_per REAL,
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
        now = datetime.datetime.now()
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today_str = datetime.datetime.now().strftime('%Y-%m-%d')
        dir_path = "/home/admin-user/server_script/Server_log_dir"
        db_path = f"{dir_path}/test_summary{today_str}.db"

        if not os.path.exists(db_path):
            yesterday = now - datetime.timedelta(days=1)
            yesterday_db = f"{dir_path}/test_summary{yesterday.strftime('%Y-%m-%d')}.db"
            yesterday_csv = f"{dir_path}/test_summary{yesterday.strftime('%Y-%m-%d')}.csv"

            if os.path.exists(yesterday_db):
                export_conn = sqlite3.connect(yesterday_db)
                export_cur = export_conn.cursor()
                export_cur.execute("SELECT * FROM daily_summary")

                with open(yesterday_csv, 'w', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    # カラム名（ヘッダー）を1行目に書き込む
                    csv_writer.writerow([desc[0] for desc in export_cur.description])
                    # データを全部書き込む
                    csv_writer.writerows(export_cur.fetchall())
                
                export_conn.close()
                
                upload_to_gcs(yesterday_csv)

            # ② 7日前の日付を計算して、サーバーから削除！（容量節約）
            seven_days_ago = now - datetime.timedelta(days=7)
            old_db = f"{dir_path}/test_summary{seven_days_ago.strftime('%Y-%m-%d')}.db"
            old_csv = f"{dir_path}/test_summary{seven_days_ago.strftime('%Y-%m-%d')}.csv"
            if os.path.exists(old_db):
                os.remove(old_db)
            if os.path.exists(old_csv):
                os.remove(old_csv)

        databace = dsql_pra.test_DB()
        summary = dsql_pra.summary_output(databace)
        #print(f"タプル{summary}")

        daily_summary_db(db_path)

        insert_data = summary + (now_str,)

        disk_conn = sqlite3.connect(db_path)
        disk_cursor = disk_conn.cursor()

        disk_cursor.execute('''
            INSERT INTO daily_summary
            (
                CPU_temp, CPU_per,
                GPU0_temp , GPU0_per ,
                GPU1_temp , GPU1_per ,
                RAM_temp, RAM_per,
                SSD_temp, LAN_temp,
                timestamp
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
        ''', insert_data)

        disk_conn.commit()
        disk_conn.close()

        #end_time = time.time()
        #syorizikan = end_time - start_time
        #print(f"処理時間：{syorizikan:.6f}秒")

