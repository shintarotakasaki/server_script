import sqlite3
import datetime
import sever_script.main_tempget as main_tempget
import sqlite_practice

def rog_DB(
        CPU_ondo,CPU_shiyouritu,
        GPU_ondo,GPU_shiyouritu,
        RAM_ondo,RAM_shiyouritu,
        SSD_ondo,
        LAN_ondo
        ):
    try:
        rogDB_conn = sqlite3.connect(':memory:')
        rogDB_cursor = rogDB_conn.cursor()
        rogDB_conn.execute('CREATE TABLE sqlite_practice (' \
        'id INTEGER PRIMARY KEY AUTOINCREMENT,' \
        'CPU_temp TEXT,CPU_per TEXT,' \
        'GPU_temp TEXT,GPU_per TEXT,' \
        'RAM_temp TEXT,RAM_per TEXT,' \
        'SSD_temp TEXT,' \
        'LAN_temp TEXT)')
        rogDB_cursor.execute('INSERT INTO temp_test(GPU_temp) VALUES(?)',(GPU_ondo))
        rogDB_conn.commit()
        return rogDB_conn

    except Exception as e:
        print(f"DB create failed...: {e}")
        return None # テスト用ダミー    

if __name__ == "__main__":
    try:
        gpu_temp = main_tempget.get_gpu_temp()
        main_conn =main_tempget.rog_DB_test(gpu_temp)
        
        if main_conn is not None:
            main_cursor = main_conn.cursor()
            main_cursor.execute('SELECT * FROM temp_test')
            print(main_cursor.fetchall())
            #main_cursor.close()
        else:
            print(f"rog_DB return:{main_conn}")

    except Exception as e:
        print(f"DB print failed...: {e}")    
