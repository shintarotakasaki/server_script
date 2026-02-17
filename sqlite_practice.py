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

        cursor.execute('CREATE TABLE sqlite_practice (' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'CPU_temp TEXT,CPU_per TEXT,' \
        'GPU_temp TEXT,GPU_per TEXT,' \
        'RAM_temp TEXT,RAM_per TEXT,' \
        'SSD_temp TEXT,' \
        'LAN_temp TEXT' \
        'timestomp  TEXT')
        #cursor.execute('INSERT INTO temp_test(GPU_temp) VALUES(?)',(GPU_ondo))
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

        gputemp_cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        gpuusage_cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"
        GPU_temp = subprocess.check_output(gputemp_cmd.split()).decode('utf-8').strip() 
        GPU_usage = subprocess.check_output(gpuusage_cmd.split()).decode('utf-8').strip() 

        RAM_temp = mtb_datas['spd5118'][0].current         # RAM ()
        ram_data = psutil.virtual_memory()
        RAM_usage = ram_data.percent

        SSD_temp = mtb_datas['nvme'][0].current            # SSD (Composite)

        LAN_temp = mtb_datas['r8169_0_b00:00'][0].current  # LAM ()
        
        NOW = datetime.datetime.now()

        return CPU_temp , CPU_usage , GPU_temp , GPU_usage , RAM_temp , RAM_usage , SSD_temp , LAN_temp , NOW
    
    except Exception as e:

        print(f"Psutil温度取得エラー{e}")
        return None , None , None , None , None , None , None , None , None
    
if __name__ == "__main__":
 
    start = time.time()
    psutil.cpu_percent(interval = None)
    Sever_datas = psutil_gettemp()
    DB = test_DB
    DB_cursor = DB.sursor()
    print({Sever_datas})
    end = time.time()

    syorizikan = end - start

    #print({sensor_datas})
    print(f"処理時間：{syorizikan:.6f}秒")
    #print("==================================")
    #print(f"CPU使用率{cpu_usage}％")
    
    #2026/2/16 ここからCPUの温度関係をどっかの関数に移動させてreturnで返させるやつを作って帰ってきたやつをfor~inでばこばこいれてsqliteに入れるやつを作れ
    #ループ処理はそのあと作ればいいや