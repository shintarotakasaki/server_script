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

        gputemp_cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        gpuusage_cmd = "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits"
        GPU_temp = float(subprocess.check_output(gputemp_cmd.split()).decode('utf-8').strip())
        GPU_usage = float(subprocess.check_output(gpuusage_cmd.split()).decode('utf-8').strip())

        RAM_temp = mtb_datas['spd5118'][0].current         # RAM ()
        ram_data = psutil.virtual_memory()
        RAM_usage = ram_data.percent

        SSD_temp = mtb_datas['nvme'][0].current            # SSD (Composite)

        LAN_temp = mtb_datas['r8169_0_b00:00'][0].current  # LAM ()
        
        NOW = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        return CPU_temp , CPU_usage , GPU_temp , GPU_usage , RAM_temp , RAM_usage , SSD_temp , LAN_temp , NOW
    
    except Exception as e:

        print(f"Psutil温度取得エラー{e}")
        return None , None , None , None , None , None , None , None , None
    
def summary_output(DB):
    
    INTERVAL_SEC = 1.0 #ログ取得間隔(1秒毎)
    COUNT_RUN = 0 #While roop カウント用
    COUNT_LIMIT = 10 #While roopカントリミット(60回)
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
                    GPU_temp , GPU_per ,
                    RAM_temp , RAM_per ,
                    SSD_temp ,
                    LAN_temp ,
                    timestamp 
 
            )VALUES(?,?,?,?,?,?,?,?,?)''',Sever_datas)
        
            DB.commit()
            COUNT_RUN += 1

            next_time += INTERVAL_SEC
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)


            if COUNT_RUN >= COUNT_LIMIT:
                    DB_cursor.execute('SELECT * FROM server_databace') #print test
                    print(DB_cursor.fetchall()) #print test
                    break
        
        elif  Sever_datas is None:
            print(f"Sever_datas is None(While roop error)")
            break
    
    DB_cursor.execute('''
        SELECT 

            ROUND(AVG(CPU_temp), 1), ROUND(AVG(CPU_per), 1),
            ROUND(AVG(GPU_temp), 1), ROUND(AVG(GPU_per), 1),
            ROUND(AVG(RAM_temp), 1), ROUND(AVG(RAM_per), 1),
            ROUND(AVG(SSD_temp), 1),
            ROUND(AVG(LAN_temp), 1)
            FROM server_databace

    ''')

    summary_data = DB_cursor.fetchone()
    DB_cursor.execete('DELETE FROM server_databace')
    DB.commit()

    return summary_data

    

if __name__ == "__main__":
    
    INTERVAL_SEC = 1.0 #ログ取得間隔(1秒毎)
    COUNT_RUN = 0 #While roop カウント用
    COUNT_LIMIT = 10 #While roopカントリミット(60回)
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
                    GPU_temp , GPU_per ,
                    RAM_temp , RAM_per ,
                    SSD_temp ,
                    LAN_temp ,
                    timestamp 
 
            )VALUES(?,?,?,?,?,?,?,?,?)''',Sever_datas)
        
            DB.commit()
            COUNT_RUN += 1

            next_time += INTERVAL_SEC
            sleep_time = next_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)


            if COUNT_RUN >= COUNT_LIMIT:
                    DB_cursor.execute('SELECT * FROM server_databace') #print test
                    print(DB_cursor.fetchall()) #print test
                    break
        
        elif  Sever_datas is None:
            print(f"Sever_datas is None(While roop error)")
            break
    
    DB_cursor.execute('''
        SELECT 

            ROUND(AVG(CPU_temp), 1), ROUND(AVG(CPU_per), 1),
            ROUND(AVG(GPU_temp), 1), ROUND(AVG(GPU_per), 1),
            ROUND(AVG(RAM_temp), 1), ROUND(AVG(RAM_per), 1),
            ROUND(AVG(SSD_temp), 1),
            ROUND(AVG(LAN_temp), 1)
            FROM server_databace

    ''')

    
    
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