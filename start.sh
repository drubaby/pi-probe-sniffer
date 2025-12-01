#!/usr/bin/bash

# Load environment variables
set -a
source .env
set +a

# Use configured USB WiFi interface from .env
WIFI_INTERFACE="${MONITOR_WIFI_INTERFACE:-wlan0}"

echo "\e[91m Killing any running probe-sniffer instances... \e[0m"
pkill -f probe_sniffer
pkill -f airodump-ng

# Check if monitor interface already exists (from previous run)
MONITOR_INTERFACE=""
for iface in $(ip link show | grep -E "^[0-9]+:" | awk '{print $2}' | tr -d ':'); do
    if [[ "$iface" == *"mon" ]]; then
        MONITOR_INTERFACE="$iface"
        echo "\e[92m Found existing monitor interface: $MONITOR_INTERFACE \e[0m"
        break
    fi
done

# If no monitor interface exists, create one with airmon-ng
if [ -z "$MONITOR_INTERFACE" ]; then
    # Check if the base interface exists
    if ! ip link show "$WIFI_INTERFACE" &> /dev/null; then
        echo "\e[91m ERROR: Interface $WIFI_INTERFACE not found! \e[0m"
        echo "Available interfaces:"
        ip link show | grep -E "^[0-9]+:" | awk '{print $2}' | tr -d ':'
        exit 1
    fi

    # Configure monitor mode using airmon-ng
    echo "\e[91m Configuring $WIFI_INTERFACE for monitor mode... \e[0m"
    sudo airmon-ng start "$WIFI_INTERFACE"

    # Find the monitor interface that was created
    for iface in $(ip link show | grep -E "^[0-9]+:" | awk '{print $2}' | tr -d ':'); do
        if [[ "$iface" == *"mon" ]]; then
            MONITOR_INTERFACE="$iface"
            echo "\e[92m Monitor interface created: $MONITOR_INTERFACE \e[0m"
            break
        fi
    done

    if [ -z "$MONITOR_INTERFACE" ]; then
        echo "\e[91m ERROR: Failed to create monitor interface! \e[0m"
        exit 1
    fi
fi

sleep 2

echo "\e[92m Starting airodump-ng on device: $MONITOR_INTERFACE in background\e[0m"
airodump-ng -K 1 "$MONITOR_INTERFACE" &> /dev/null &
sleep 2

echo "\e[92m Starting probe-sniffer on $MONITOR_INTERFACE...\e[0m"
python -m probe_sniffer -m "$MONITOR_INTERFACE"
