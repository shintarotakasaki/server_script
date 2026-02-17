import sqlite3
#import datetime
import subprocess

#sudo systemctl set-default multi-user.target
#sudo systemctl set-default graphical.target

#GPUの温度を取得する
def get_gpu_temp():
    try:
        # nvidia-smiから温度を取得
        cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        temp = subprocess.check_output(cmd.split()).decode('utf-8').strip() 
        print(f"success get gpu_temp!{temp} *C")        
        return temp
    except Exception as e:
        print(f"GPUtemp get as false...: {e}")
        return "-114514" # テスト用ダミーdef get_gpu_temp():

def rog_DB_test(gpu_kaeriti):
    try:
        #GPU用のDBを作成
        gpu_conn = sqlite3.connect(':memory:')
        gpu_cursor = gpu_conn.cursor()
        gpu_cursor.execute('CREATE TABLE temp_test (id INTEGER PRIMARY KEY AUTOINCREMENT, gpu_temp TEXT)')
        gpu_cursor.execute('INSERT INTO temp_test(gpu_temp) VALUES(?)',(gpu_kaeriti,))
        gpu_conn.commit()
        return gpu_conn
    except Exception as e:
        print(f"DB create failed...: {e}")
        return None # テスト用ダミー

    

if __name__ == "__main__":
    #print(f"Hellow Wold!")
    current_temp = get_gpu_temp()
    print_test = rog_DB_test(current_temp)

    if print_test is None:
        print(f"DB ceate failed...(__name__=__main__):")
    else:
        print_test_cursor = print_test.cursor()
        print_test_cursor.execute('SELECT * FROM temp_test')
        print(print_test_cursor.fetchall())
        print_test.close()
