from dotenv import load_dotenv
import os

load_dotenv()

MQTT_BROKER_URL = "192.168.0.2"
MQTT_BROKER_PORT = 1883

PROBE_TOPIC = "wudsPi/probe"
STATUS_TOPIC = "wudsPi/status"

# Discord Notification Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

DISCORD_ENABLED = True
DISCORD_DRY_RUN = False  # Set False for real notifications
DISCORD_RETURNING_THRESHOLD_HOURS = 24
