import subprocess
import time

# import signal
import zoneinfo
from datetime import datetime

import boto3


wasabi = boto3.client(
    "s3",
    endpoint_url=f"https://s3.{REGION_NAME}.wasabisys.com",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_ACCESS_KEY,
)

user_id = ""
while True:
    print("download.sh を起動します。")
    date = datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d_%H-%M")
    process = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-i",
            f"http://twitcasting.tv/{user_id}/metastream.m3u8/?video=1",
            "-c",
            "copy",
            "-map",
            "p:0",
            "{user_id}_{date}.mp4",
        ]
    )
    print(f"PID: {process.pid}")

    time.sleep(5)

    if process.poll() is None:
        print("配信始めたぞあいつ")
        # process.send_signal(signal.SIGUSR1)

    process.wait()

    time.sleep(5)
