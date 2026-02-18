import sqlite3
import datetime
import os
import main_tempget
import sqlite_practice

def Daily_DB(Sever_datas):
    try:
        rogDB_conn = sqlite3.connect(':memory:')
        rogDB_cursor = rogDB_conn.cursor()
        rogDB_cursor.execute('CREATE TABLE IF NOT EXISTS temp_test (id INTEGER PRIMARY KEY AUTOINCREMENT, gpu_temp TEXT)')
        rogDB_cursor.execute('INSERT INTO temp_test(gpu_temp) VALUES(?)',(Sever_datas))
        rogDB_conn.commit()
        return rogDB_conn

    except Exception as e:
        print(f"DB create failed...: {e}")
        return None # テスト用ダミー    

if __name__ == "__main__":
    try:
        gpu_temp = sqlite_practice.psutil_gettemp()
        main_conn =sqlite_practice.test_DB()
        
        if main_conn is not None:
            main_cursor = main_conn.cursor()
            main_cursor.execute('SELECT * FROM temp_test')
            print(main_cursor.fetchall())
            #main_cursor.close()
        else:
            print(f"rog_DB return:{main_conn}")

    except Exception as e:
        print(f"DB print failed...: {e}")    
