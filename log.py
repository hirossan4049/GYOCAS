import json
import logging
import urllib.request
from datetime import datetime

logger = logging.getLogger("GYOCAS")
logger.setLevel(logging.DEBUG)

mapping = {
  "TRACE": "[TRACE ]",
  "DEBUG": "[\x1b[0;36mDEBUG\x1b[0m ]",
  "INFO": "[\x1b[0;32mINFO\x1b[0m  ]",
  "WARNING": "[\x1b[0;33mWARN\x1b[0m  ]",
  "WARN": "[\x1b[0;33mWARN\x1b[0m  ]",
  "ERROR": "\x1b[0;31m[ERROR ]\x1b[0m",
  "ALERT": "\x1b[0;37;41m[ALERT ]\x1b[0m",
  "CRITICAL": "\x1b[0;37;41m[CRTCL ]\x1b[0m",
}


class ColorfulHandler(logging.StreamHandler):
  def emit(self, record: logging.LogRecord) -> None:
    record.levelname = mapping.get(record.levelname, record.levelname)
    super().emit(record)


logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)

# Webhook URL は setWebhookURL() で設定
WEBHOOK_URL = None


def setWebhookURL(url):
  global WEBHOOK_URL
  WEBHOOK_URL = url


# ログレベルごとの Discord embed 用の色マッピング
DISCORD_COLOR_MAPPING = {
  logging.DEBUG: 3447003,  # 青
  logging.INFO: 3066993,  # 緑
  logging.WARNING: 15105570,  # オレンジ
  logging.ERROR: 15158332,  # 赤
  logging.CRITICAL: 10038562,  # 暗めの赤
}


class DiscordLogHandler(logging.Handler):
  """DEBUG～CRITICAL のログを Discord Webhook に送信するハンドラ"""

  def __init__(self, level=logging.NOTSET):
    super().__init__(level)

  def emit(self, record: logging.LogRecord) -> None:
    if WEBHOOK_URL is None:
      return  # Webhook URL 未設定の場合は何もしない
    try:
      # フォーマッタを使ってメッセージを作成
      msg = self.format(record)
      # レベルに応じた色を設定（なければデフォルト色 7506394）
      color = DISCORD_COLOR_MAPPING.get(record.levelno, 7506394)
      embed = {
        "title": record.name,
        "description": msg,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
      }
      payload = {"embeds": [embed]}
      data = json.dumps(payload).encode("utf-8")
      headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python/urllib (DiscordWebhook script)",
      }
      req = urllib.request.Request(WEBHOOK_URL, data=data, headers=headers)
      with urllib.request.urlopen(req) as response:
        # 正常時、Discord は 204 (No Content) を返す
        if response.getcode() != 204:
          logger.error(f"Failed to send webhook: {response.getcode()}")
    except Exception as e:
      logger.error(f"Exception in sending webhook: {e}")


# Discord 用のハンドラを作成し、フォーマッタを設定
discord_handler = DiscordLogHandler()
discord_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
discord_handler.setFormatter(formatter)
logger.addHandler(discord_handler)

D = logger.debug
I = logger.info
W = logger.warning
E = logger.error
C = logger.critical

if __name__ == "__main__":
  # 自分の Discord Webhook URL を設定してください
  setWebhookURL("https://discord.com/api/webhooks/ひみつだよ〜")

  # 各ログレベルでテスト
  logger.debug("これはデバッグメッセージです。")
  logger.info("これはインフォメーションメッセージです。")
  logger.warning("これは警告メッセージです。")
  logger.error("これはエラーメッセージです。")
  logger.critical("これはクリティカルメッセージです。")
