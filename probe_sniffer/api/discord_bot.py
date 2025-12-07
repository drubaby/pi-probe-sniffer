"""Discord bot for interactive notifications."""

import logging
import discord
from discord import ui
from datetime import datetime, timezone

from probe_sniffer import config
from probe_sniffer.storage.queries import disable_fingerprint_notifications, set_fingerprint_alias

logger = logging.getLogger("DISCORD_BOT")


def format_local_time(utc_timestamp_str: str) -> str:
    """Convert UTC timestamp string from database to local time."""
    if not utc_timestamp_str or utc_timestamp_str == "Unknown":
        return "Unknown"

    try:
        # Parse the ISO format timestamp (stored as UTC in database)
        utc_dt = datetime.fromisoformat(utc_timestamp_str).replace(tzinfo=timezone.utc)
        # Convert to local timezone
        local_dt = utc_dt.astimezone()
        # Format: "Dec 07, 2:30:45 PM"
        return local_dt.strftime("%b %d, %I:%M:%S %p")
    except (ValueError, TypeError):
        return utc_timestamp_str  # Return original if parsing fails


class AliasModal(ui.Modal, title="Set Device Alias"):
    """Modal for entering a device alias."""

    alias_input = ui.TextInput(
        label="Alias",
        placeholder="e.g. John's iPhone, Neighbor TV",
        max_length=100,
    )

    def __init__(self, fingerprint_id: str, button: ui.Button):
        super().__init__()
        self.fingerprint_id = fingerprint_id
        self.button = button

    async def on_submit(self, interaction: discord.Interaction):
        alias = self.alias_input.value.strip()
        set_fingerprint_alias(self.fingerprint_id, alias)

        # Update the button to show the alias was set
        self.button.label = f"✏️ {alias[:20]}"
        self.button.disabled = True
        await interaction.response.edit_message(view=self.button.view)
        logger.info(f"Set alias '{alias}' for fingerprint: {self.fingerprint_id[:16]}...")


class NotificationView(ui.View):
    """View with Silence and Alias buttons for device notifications."""

    def __init__(self, fingerprint_id: str):
        super().__init__(timeout=None)  # Persistent across restarts
        self.fingerprint_id = fingerprint_id

    @ui.button(label="🔇 Silence", style=discord.ButtonStyle.secondary)
    async def silence(self, interaction: discord.Interaction, button: ui.Button):
        disable_fingerprint_notifications(self.fingerprint_id)

        button.disabled = True
        button.label = "🔇 Silenced"
        await interaction.response.edit_message(view=self)
        logger.info(f"Silenced notifications for fingerprint: {self.fingerprint_id[:16]}...")

    @ui.button(label="✏️ Alias", style=discord.ButtonStyle.primary)
    async def set_alias(self, interaction: discord.Interaction, button: ui.Button):
        modal = AliasModal(self.fingerprint_id, button)
        await interaction.response.send_modal(modal)


def build_embed(fingerprint: dict, probe_data: dict, notification_type: str) -> discord.Embed:
    """Build a Discord embed for a device notification."""
    if notification_type == "new":
        title = "🆕 New Device Detected"
        color = discord.Color.blurple()
    else:
        title = "🔄 Device Returned"
        color = discord.Color.green()

    embed = discord.Embed(title=title, color=color, timestamp=datetime.utcnow())

    embed.add_field(name="Manufacturer", value=probe_data.get("oui", "Unknown"), inline=True)
    embed.add_field(name="Signal", value=f"{probe_data.get('dbm', 'N/A')} dBm", inline=True)
    embed.add_field(
        name="Sighting Count", value=str(fingerprint.get("sighting_count", 0)), inline=True
    )
    embed.add_field(
        name="First Seen", value=format_local_time(fingerprint.get("first_seen")), inline=True
    )

    if notification_type == "returning":
        embed.add_field(
            name="Last Seen", value=format_local_time(fingerprint.get("last_seen")), inline=True
        )

    ssid = probe_data.get("ssid", "Undirected Probe")
    embed.add_field(name="Currently Probing", value=ssid, inline=False)

    fingerprint_id = fingerprint.get("fingerprint_id", "Unknown")
    embed.set_footer(text=f"Fingerprint: {fingerprint_id[:16]}...")

    return embed


class SnifferBot(discord.Client):
    """Discord bot that sends device notifications with interactive buttons."""

    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.channel = None

    async def on_ready(self):
        self.channel = self.get_channel(config.DISCORD_CHANNEL_ID)
        if self.channel:
            logger.info(f"Bot connected as {self.user}, channel: #{self.channel.name}")
        else:
            logger.warning(f"Bot connected as {self.user}, but channel ID {config.DISCORD_CHANNEL_ID} not found")

    async def send_notification(self, fingerprint: dict, probe_data: dict, notification_type: str):
        """Send a notification to the configured Discord channel."""
        if not self.is_ready():
            raise RuntimeError(f"Bot not ready (is_closed={self.is_closed()}, user={self.user})")

        if not self.channel:
            raise RuntimeError(f"Channel not found (ID={config.DISCORD_CHANNEL_ID})")

        embed = build_embed(fingerprint, probe_data, notification_type)
        view = NotificationView(fingerprint["fingerprint_id"])
        await self.channel.send(embed=embed, view=view)
        logger.info(f"Sent {notification_type} notification for {fingerprint['fingerprint_id'][:16]}...")


bot = SnifferBot()
