import subprocess
import datetime

def get_log_GPU():

    #GPU温度取得
    try:
        # nvidia-smiから温度を取得
        cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        gpu_temp = subprocess.check_output(cmd.split()).decode('utf-8').strip()
        return gpu_temp
    except Exception as e:
        print(f"GPUtemp get as false...: {e}")
        return "99" # テスト用ダミー
    