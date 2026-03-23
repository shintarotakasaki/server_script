import sqlite3
import datetime
import psutil
import time
import subprocess
import random

"""
def get_cpu_rog():
    cmd_cpu_ondo = "cat /sys/class/thermal/thermal_zone0/temp"
    cmd_cpu_shiyouritu = "env LC_ALL=C top -b -n 1"
"""

def test_DB():
    
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE server_databace (
        
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                CPU_temp REAL,CPU_per REAL,
                GPU0_temp REAL, GPU0_per REAL,
                GPU1_temp REAL, GPU1_per REAL,
                RAM_temp REAL,RAM_per REAL,
                SSD_temp REAL,
                LAN_temp REAL,
                timestamp  TEXT
        
            )''')
        
        
        #DB_cursor.execute('''
            #INSERT INTO server_databace(
                            
                #CPU_temp , CPU_per ,
                #GPU_temp , GPU_per ,
                #RAM_temp , RAM_per ,
                #SSD_temp ,
                #LAN_temp ,
                #timestamp 
 
        #)VALUES(?,?,?,?,?,?,?,?,?)''',)
        

        conn.commit()

        return conn
    
    except Exception as e:
        print(f"DB作れてないよ: {e}")
        return None # テスト用ダミー  
    
def psutil_gettemp():

    try:

        mtb_datas = psutil.sensors_temperatures()

        CPU_temp = mtb_datas['k10temp'][0].current         # CPU (Tctl)
        CPU_usage = psutil.cpu_percent(interval = None)
# (中略) CPUの取得の下あたりから書き換え
        gputemp_cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        gpuusage_cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"
        
        # 改行(\n)で切り分けて配列にする
        gpu_temps_str = subprocess.check_output(gputemp_cmd.split()).decode('utf-8').strip().split('\n')
        gpu_usage_str = subprocess.check_output(gpuusage_cmd.split()).decode('utf-8').strip().split('\n')

        # 0番目と1番目をそれぞれ取得
        GPU0_temp = float(gpu_temps_str[0])
        GPU1_temp = float(gpu_temps_str[1]) if len(gpu_temps_str) > 1 else 0.0
        
        GPU0_usage = float(gpu_usage_str[0])
        GPU1_usage = float(gpu_usage_str[1]) if len(gpu_usage_str) > 1 else 0.0

        RAM_temp = mtb_datas['spd5118'][0].current         # RAM ()
        ram_data = psutil.virtual_memory()
        RAM_usage = ram_data.percent

        SSD_temp = mtb_datas['nvme'][0].current            # SSD (Composite)

        LAN_temp = mtb_datas['r8169_0_b00:00'][0].current  # LAM ()
        
        NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        return CPU_temp , CPU_usage , GPU0_temp , GPU0_usage ,GPU1_temp , GPU1_usage , RAM_temp , RAM_usage , SSD_temp , LAN_temp , NOW
    
    except Exception as e:
        # 2. ★ここがモック化！メインPCだと nvidia-smi が無いので絶対ここに飛んでくる
        #print(f"[テストモード] ハードウェア情報が取れないためダミーデータを使用します。理由: {e}")
        
        # メインPC用に、それっぽいダミーデータをでっち上げる（randomでそれっぽく）
        dummy_cpu_temp = round(random.uniform(40.0, 50.0), 1)
        dummy_cpu_per  = round(random.uniform(10.0, 30.0), 1)
        dummy_gpu0_temp = 55.0
        dummy_gpu0_per  = 100.0
        dummy_gpu1_temp = 52.0
        dummy_gpu1_per  = 98.0
        dummy_ram_temp  = 45.0
        dummy_ram_per   = 60.0
        dummy_ssd_temp  = 38.0
        dummy_lan_temp  = 40.0
        
        NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 本番と同じ数の項目（11個）を返す
        return (dummy_cpu_temp, dummy_cpu_per, 
                dummy_gpu0_temp, dummy_gpu0_per, 
                dummy_gpu1_temp, dummy_gpu1_per, 
                dummy_ram_temp, dummy_ram_per, 
                dummy_ssd_temp, dummy_lan_temp, 
                NOW)

def summary_output(DB):
    
    INTERVAL_SEC = 1.0 #ログ取得間隔(1秒毎)
    COUNT_RUN = 0 #While roop カウント用
    COUNT_LIMIT = 60 #While roopカントリミット(60回)
    #start_time = time.time()
    next_time = time.time()
    psutil.cpu_percent(interval = None)

    DB_cursor = DB.cursor()

    while True:
        Sever_datas = psutil_gettemp()
        if Sever_datas is not None:

            DB_cursor.execute('''
                INSERT INTO server_databace(
                            
                    CPU_temp , CPU_per ,
                    GPU0_temp , GPU0_per ,
                    GPU1_temp , GPU1_per ,
                    RAM_temp , RAM_per ,
                    SSD_temp ,
                    LAN_temp ,
                    timestamp 
 
            )VALUES(?,?,?,?,?,?,?,?,?,?,?)''',Sever_datas)
        
            DB.commit()
            COUNT_RUN += 1

            next_time += INTERVAL_SEC
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)


            if COUNT_RUN >= COUNT_LIMIT:
                    #DB_cursor.execute('SELECT * FROM server_databace') #print test
                    #print(DB_cursor.fetchall()) #print test
                    break
        
        elif  Sever_datas is None:
            print(f"Sever_datas is None(While roop error)")
            break
    
    DB_cursor.execute('''
        SELECT 

            ROUND(AVG(CPU_temp), 1), ROUND(AVG(CPU_per), 1),
            ROUND(AVG(GPU0_temp), 1), ROUND(AVG(GPU0_per), 1),
            ROUND(AVG(GPU1_temp), 1), ROUND(AVG(GPU1_per), 1),
            ROUND(AVG(RAM_temp), 1), ROUND(AVG(RAM_per), 1),
            ROUND(AVG(SSD_temp), 1),
            ROUND(AVG(LAN_temp), 1)
            FROM server_databace

    ''')
    
    summary_data = DB_cursor.fetchone()
    DB_cursor.execute('DELETE FROM server_databace')
    DB.commit()

    return summary_data

    

if __name__ == "__main__":
    
    INTERVAL_SEC = 1.0 #ログ取得間隔(1秒毎)
    COUNT_RUN = 0 #While roop カウント用
    COUNT_LIMIT = 3 #While roopカントリミット(60回)
    #start_time = time.time()
    next_time = time.time()
    psutil.cpu_percent(interval = None)

    DB = test_DB()
    DB_cursor = DB.cursor()

    while True:
        Sever_datas = psutil_gettemp()
        if Sever_datas is not None:

            DB_cursor.execute('''
                INSERT INTO server_databace(
                            
                    CPU_temp , CPU_per ,
                    GPU0_temp , GPU0_per ,
                    GPU1_temp , GPU1_per ,
                    RAM_temp , RAM_per ,
                    SSD_temp ,
                    LAN_temp ,
                    timestamp 
 
            )VALUES(?,?,?,?,?,?,?,?,?,?,?)''',Sever_datas)
        
            DB.commit()
            COUNT_RUN += 1

            next_time += INTERVAL_SEC
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)


            if COUNT_RUN >= COUNT_LIMIT:
                    DB_cursor.execute('SELECT * FROM server_databace') #print test
                    print(f"server datas is{DB_cursor.fetchall()}") #print test
                    break
        
        elif  Sever_datas is None:
            print(f"Sever_datas is None(While roop error)")
            break
    
    DB_cursor.execute('''
        SELECT 

            ROUND(AVG(CPU_temp), 1), ROUND(AVG(CPU_per), 1),
            ROUND(AVG(GPU0_temp), 1), ROUND(AVG(GPU0_per), 1),
            ROUND(AVG(GPU1_temp), 1), ROUND(AVG(GPU1_per), 1),
            ROUND(AVG(RAM_temp), 1), ROUND(AVG(RAM_per), 1),
            ROUND(AVG(SSD_temp), 1),
            ROUND(AVG(LAN_temp), 1)
            FROM server_databace

    ''')
    print(f"DB summary is{DB_cursor.fetchall()}") 

    
    
    #print(f"サマリー{DB_cursor.fetchall()}")

    #end_time = time.time()

    #syorizikan = end_time - start_time

    #print({sensor_datas})
    #print(f"処理時間：{syorizikan:.6f}秒")
    #print("==================================")
    #print(f"CPU使用率{cpu_usage}％")
    
    #2026/2/16 ここからCPUの温度関係をどっかの関数に移動させてreturnで返させるやつを作って帰ってきたやつをfor~inでばこばこいれてsqliteに入れるやつを作れ
    #ループ処理はそのあと作ればいいや

    #2026/2/18 sqlやっとできた...

    #2026/2/19 なんかループが思った以上にサクっとできてびっくりしている、成長しているのか？？？
    #※AIのおかげだから増長しないように