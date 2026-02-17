import subprocess
import datetime
from google.cloud import storage

# 【重要】ここを自分のバケット名に書き換えてください
BUCKET_NAME = 'linux-server-1'

def get_gpu_temp():
    try:
        # nvidia-smiから温度を取得
        cmd = "nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits"
        temp = subprocess.check_output(cmd.split()).decode('utf-8').strip()
        return temp
    except Exception as e:
        print(f"GPUtemp get as false...: {e}")
        return "99" # テスト用ダミー

def upload_to_gcs(text_data):
    try:
        # 環境変数から認証情報を読み込み
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'gpu_logs/temp_{now}.txt'

        blob = bucket.blob(filename)
        blob.upload_from_string(f"Temperature: {text_data}C")

        print(f"success!://{BUCKET_NAME}/{filename}")
    except Exception as e:
        print(f"false...: {e}")

if __name__ == "__main__":
    print("--- GPUtemoget & starting tempupload ---")
    current_temp = get_gpu_temp()
    print(f"gputemp as: {current_temp}")
    upload_to_gcs(current_temp)