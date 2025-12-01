import argparse
import csv
import json
import logging
import random
import sys
from pathlib import Path
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

from scapy.all import sniff, Dot11ProbeReq
from paho.mqtt import client as mqtt_client, enums as paho_enums

from probe_sniffer import config
from probe_sniffer.storage.database import init_database
from probe_sniffer.storage.queries import get_trusted_devices, log_sighting
from probe_sniffer.utils import probe_utils, time_utils
from probe_sniffer.models.probe import Probe

load_dotenv()

logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
# sniff_logs logs start times and errors
import os

sniff_logs = os.getenv("LOG_PATH", "/var/log/probe-sniffer/sniffer.log")
general_logger = logging.getLogger("GENERAL")
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)
# Create log directory if it doesn't exist
Path(sniff_logs).parent.mkdir(parents=True, exist_ok=True)
handler = logging.FileHandler(sniff_logs, mode="a")
handler.setFormatter(formatter)
general_logger.addHandler(handler)

CSVDelim = ","

# sb_client = supabase_utils.create_supabase_client()

# Python Dict built to hold all known devices and known mac->manufacturer designations
OUIMEM = {}


def build_oui_lookup() -> None:
    """
    Builds OUIMEM dictionary for quick manufacturer lookup.
    First adds trusted device *full mac addresses* from SQLite to the dictionary before adding all manufacturers from saved OUI.txt file
    Eventually it would be good to curl OUI.txt from wireshark each day...
    """
    try:
        # Fetch trusted devices from SQLite
        trusted_macs = get_trusted_devices()
        for mac in trusted_macs:
            OUIMEM[mac.lower()] = "Trusted Device"
    except Exception as e:
        general_logger.error(f"Failed to fetch trusted devices: {e}")

    # Get path to data/OUI.txt from package root
    oui_file = Path(__file__).parent.parent / "data" / "OUI.txt"

    with open(
        oui_file,
        "r",
    ) as OUILookup:
        for line in csv.reader(OUILookup, delimiter="\t"):
            if not line or line[0][0] == "#":
                continue
            else:
                OUIMEM[line[0].rstrip(" ")] = line[2]


# JSON encode probe for mqtt. Probably should get refactored.
def probe_json(probe: list):
    return json.dumps(
        {
            "timestamp": probe[0],
            "rssi": probe[1],
            "channel": probe[2],
            "MAC": probe[3],
            "clientOUI": probe[4],
            "BSSID": probe[5],
        }
    )


"""
Connect to MQTT broker
"""
# broker = os.getenv("MQTT_BROKER_URL")
broker = config.MQTT_BROKER_URL
port = config.MQTT_BROKER_PORT
topic = config.PROBE_TOPIC
status_topic = config.STATUS_TOPIC


def connect_mqtt():
    client_id = f"wudsPi-{random.randint(0, 1000)}"

    # Set Connecting Client ID
    client = mqtt_client.Client(
        paho_enums.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt_client.MQTTv5
    )

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            general_logger.info(f"Connected to MQTT Broker with client id: {client_id}")
            client.publish(status_topic, "Online", qos=1, retain=True)
            general_logger.info("Client connected flag: " + str(client.is_connected()))
        else:
            general_logger.warn("Failed to connect, return code %d\n", reason_code)

    def on_disconnect(client, userdata, reason_code, properties):
        general_logger.warn("Disconnected result code: " + str(reason_code))

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Set LWT for client if it goes down
    client.will_set(status_topic, payload="Offline", qos=1, retain=True)
    client.connect(broker, port, 60, clean_start=False)

    client.loop_start()
    # client.publish(status_topic, "Online", qos=1, retain=True)
    return client


# Rotating logger and data formatting based on packet type
def probe_log_build(logger: logging):

    # Instantiate MQTT Client
    C = connect_mqtt()

    def probe_handler(packet):
        radio = str(packet.mysummary)
        log_time = time_utils.get_log_time()

        MAC = str(packet.addr2).upper()
        clientOUI = MAC[:8]
        firstOctet = clientOUI[:2]
        binaryRep = probe_utils.binaryrep(firstOctet)

        # We're only concerned with wifi probes, i.e. packets with Dot11ProbeReq layer
        if packet.haslayer(Dot11ProbeReq):

            # Handle trusted devices: if *full MAC address* is found in OUIMEM it came from the trusted device table
            if OUIMEM.get(MAC.lower()):
                # Noisy to actually log this but uncomment to debug
                # general_logger.info(f"{OUIMEM.get(MAC.lower())} seen")
                pass
            else:
                probe = [
                    log_time,
                    probe_utils.rssi(radio),
                    str(probe_utils.get_channel_number(radio)),
                    MAC.lower(),
                ]
                probe_class = Probe(
                    log_time,
                    probe_utils.get_dBm(radio),
                    probe_utils.get_channel_number(radio),
                    MAC.lower(),
                )

                if OUIMEM.get(clientOUI) is not None:
                    probe.append(OUIMEM.get(clientOUI))
                    probe_class.oui = OUIMEM.get(clientOUI)
                else:
                    if binaryRep[6:7] == "1":
                        probe.append("Locally Assigned")
                        probe_class.oui = "Locally Assigned"
                    else:
                        probe.append("Unknown OUI")
                        probe_class.oui = "Unknown OUI"
                try:
                    if "\x00" not in packet[Dot11ProbeReq].info.decode("utf-8", "ignore"):
                        if str(packet.info):
                            decoded = str(packet.info.decode("utf-8", "ignore"))
                            BSSID = decoded if decoded != "" else "Undirected Probe"
                            probe.append(BSSID)
                            probe_class.ssid = BSSID
                except UnicodeDecodeError:
                    general_logger.error(
                        "Unicode decode error: ",
                        packet[Dot11ProbeReq].info.decode("utf-8", "ignore"),
                    )

                # Logger writes probe to local CSV file (and STDOUT)
                logger.info(probe_class.to_csv())
                # MQQT Client publishes json-encoded data to broker
                C.publish(topic, probe_class.mqtt_json())
                # Save sighting to SQLite database
                try:
                    log_sighting(probe_class.to_sighting_dto())
                except Exception as e:
                    general_logger.error(f"Failed to save sighting: {e}")

    return probe_handler


def main():
    # Arguments for terminal control
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--monitor")
    args = parser.parse_args()

    if not args.monitor:
        print("Monitor mode adapter not set with -m flag")
        sys.exit(-1)

    general_logger.info("**** Sniff script started ****")

    # Initialize SQLite database
    init_database()

    logger = logging.getLogger("PROBES")
    # Output location
    # handler = RotatingFileHandler(str(args.file) + ".csv")
    # logger.addHandler(handler)
    # logger.addHandler(logging.StreamHandler(sys.stdout))

    build_oui_lookup()

    try:
        sniff(iface=args.monitor, prn=probe_log_build(logger), store=0)
    except Exception as e:
        general_logger.warning(type(e))
        general_logger.exception(e)
        sys.exit(-1)


if __name__ == "__main__":
    main()
