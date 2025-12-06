from dotenv import load_dotenv
import os

load_dotenv()

MQTT_BROKER_URL = "192.168.0.2"
MQTT_BROKER_PORT = 1883

PROBE_TOPIC = "wudsPi/probe"
STATUS_TOPIC = "wudsPi/status"

# Discord Notification Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
DISCORD_ENABLED = True
DISCORD_DRY_RUN = False  # Set False for real notifications
DISCORD_RETURNING_THRESHOLD_HOURS = 24
