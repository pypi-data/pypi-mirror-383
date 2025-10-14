import os
# 当前文件夹上层的.evn文件

EOS_APPID=os.getenv("EOS_APPID")
EOS_SECRET=os.getenv("EOS_SECRET")
EOS_BUCKETID=os.getenv("EOS_BUCKETID")
EOS_URL=os.getenv("EOS_URL")
EOS_TOKEN_URL=os.getenv("EOS_TOKEN_URL")
EOS_SAVE_DATA_URL=os.getenv("EOS_SAVE_DATA_URL")
EOS_ONLINE_URL=os.getenv("EOS_ONLINE_URL")
UPLOAD_TEMP_PATH=os.getenv("UPLOAD_TEMP_PATH", '/tmp/upload_temp')

MODE = os.getenv('MODE', "dev")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT= os.getenv("REDIS_PORT")
REDIS_PASSWORD= os.getenv("REDIS_PASSWORD", "123456")

# STATIC_URL = os.getenv()
PORT = os.getenv("PORT", "8188")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "input")
# LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

TASK_STATUS_PREFIX = os.getenv("TASK_STATUS_PREFIX", "aigc_comfy_task_status:")

TASK_QUEUE_KEY = os.getenv("TASK_QUEUE_KEY", "aigc_comfy_task_queue")
TASK_DATA_PREFIX = os.getenv("TASK_DATA_PREFIX", "aigc_comfy_task_data:")
