import sqlite3
import datetime
import psutil
import time
import subprocess

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
                GPU_temp REAL,GPU_per REAL,
                RAM_temp REAL,RAM_per REAL,
                SSD_temp REAL,
                LAN_temp REAL,
                timestamp  TEXT
        
            )''')
        

        return conn
    
    except Exception as e:
        print(f"DB作れてないよ: {e}")
        return None # テスト用ダミー  
    
def psutil_gettemp():

    try:

        mtb_datas = psutil.sensors_temperatures()

        CPU_temp = mtb_datas['k10temp'][0].current         # CPU (Tctl)
        CPU_usage = psutil.cpu_percent(interval = None)

        gputemp_cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        gpuusage_cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"
        GPU_temp = float(subprocess.check_output(gputemp_cmd.split()).decode('utf-8').strip())
        GPU_usage = float(subprocess.check_output(gpuusage_cmd.split()).decode('utf-8').strip())

        RAM_temp = mtb_datas['spd5118'][0].current         # RAM ()
        ram_data = psutil.virtual_memory()
        RAM_usage = ram_data.percent

        SSD_temp = mtb_datas['nvme'][0].current            # SSD (Composite)

        LAN_temp = mtb_datas['r8169_0_b00:00'][0].current  # LAM ()
        
        NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return CPU_temp , CPU_usage , GPU_temp , GPU_usage , RAM_temp , RAM_usage , SSD_temp , LAN_temp , NOW
    
    except Exception as e:

        print(f"Psutil温度取得エラー{e}")
        return None , None , None , None , None , None , None , None , None
    
if __name__ == "__main__":
 
    start = time.time()
    psutil.cpu_percent(interval = None)
    Sever_datas = psutil_gettemp()
    DB = test_DB()
    DB_cursor = DB.cursor()
    DB_cursor.execute('''
        INSERT INTO server_databace(
                            
            CPU_temp , CPU_per ,
            GPU_temp , GPU_per ,
            RAM_temp , RAM_per ,
            SSD_temp ,
            LAN_temp ,
            timestamp 
 
        )VALUES(?,?,?,?,?,?,?,?,?)''',Sever_datas)
    DB.commit()
    DB_cursor.execute('SELECT * FROM server_databace')
    #print(DB_cursor.fetchall())

    end = time.time()

    syorizikan = end - start

    #print({sensor_datas})
    print(f"処理時間：{syorizikan:.6f}秒")
    #print("==================================")
    #print(f"CPU使用率{cpu_usage}％")
    
    #2026/2/16 ここからCPUの温度関係をどっかの関数に移動させてreturnで返させるやつを作って帰ってきたやつをfor~inでばこばこいれてsqliteに入れるやつを作れ
    #ループ処理はそのあと作ればいいや