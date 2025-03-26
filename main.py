#!/usr/bin/env -S uv run -s
import os
import signal
import subprocess
import time
import zoneinfo
from datetime import datetime

import boto3
from dotenv import load_dotenv

import log

log.I("hello GYOCAS!")

load_dotenv()

REGION_NAME = os.environ.get("REGION_NAME")
S3_BUCKET = os.environ.get("S3_BUCKET")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")
S3_DIR = os.environ.get("S3_DIR")
USER_ID = os.environ.get("USER_ID")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not USER_ID:
  log.C("USER_ID NOT FOUND")
else:
  log.setWebhookURL(WEBHOOK_URL)

log.I(f"[WATCH USER_ID ]: @{USER_ID}")
log.I(f"[Webhook Notify]: {WEBHOOK_URL is not None}")

wasabi = boto3.client(
  "s3",
  endpoint_url=f"https://s3.{REGION_NAME}.wasabisys.com",
  aws_access_key_id=ACCESS_KEY,
  aws_secret_access_key=SECRET_ACCESS_KEY,
)


def download():
  return subprocess.Popen(
    [
      "ffmpeg",
      "-y",
      "-i",
      f"http://twitcasting.tv/{USER_ID}/metastream.m3u8/?video=1",
      "-c",
      "copy",
      "-map",
      "p:0",
      filename,
    ]
  )


def notify():
  if not WEBHOOK_URL:
    return


try:
  while True:
    print("download.sh を起動します。")
    date = datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d_%H-%M")
    filename = f"{USER_ID}_{date}.mp4"
    process = download()
    print(f"PID: {process.pid}")

    time.sleep(5)
    isLive = False
    if process.poll() is None:
      isLive = True
      log.I(f"{USER_ID}が配信を始めました")
      # 1セクション目は音がなく、そのまま音無しで録画されてしまうため、いったんキャンセルする。
      time.sleep(20)
      process.send_signal(signal.SIGUSR1)
      process = download()

    process.wait()
    if isLive:
      log.I(f"`{filename}`が配信を終えました。アップロードを開始します")
      try:
        wasabi.upload_file(filename, S3_BUCKET, f"{USER_ID}/{filename}")
      except Exception as e:
        log.E(f"アップロードに失敗しました:{e}")
      finally:
        log.I(f"`{filename}`アップロード完了")

    time.sleep(5)
except Exception as e:
  log.C(f"落ちた:{e}")
