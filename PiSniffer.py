import argparse
import csv
import json
import logging
import os
import sys
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import random
import config

from scapy.all import sniff, Dot11ProbeReq, DHCP

from paho.mqtt import client as mqtt_client, enums as paho_enums

from utils import probes, time
from db import supabase_utils

load_dotenv()

logging.basicConfig(
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
# sniff_logs logs start times and errors to usb
sniff_logs = "/usb/sniff_log.log"
general_logger = logging.getLogger("GENERAL")
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)
handler = logging.FileHandler(sniff_logs, mode="a")
handler.setFormatter(formatter)
general_logger.addHandler(handler)

CSVDelim = ","

sb_client = supabase_utils.create_supabase_client()

# Python Dict built to hold all known devices and known mac->manufacturer designations
OUIMEM = {}


def build_oui_lookup() -> None:
    """
    Builds OUIMEM dictionary for quick manufacturer lookup.
    First adds trusted device *full mac addresses* from supabase table to the dictionary before adding all manufacturers from saved OUI.txt file
    Eventually it would be good to curl OUI.txt from wireshark each day...
    """
    try:
        trusted = supabase_utils.get_trusted_devices(sb_client)
        for item in json.loads(trusted):
            OUIMEM[item["mac"].lower()] = item["name"]
    except:
        general_logger.error("Failed to fetch trusted devices")

    with open(
        "OUI.txt",
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
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            general_logger.info("Connected to MQTT Broker")
        else:
            general_logger.warn("Failed to connect, return code %d\n", reason_code)

    def on_disconnect(client, userdata, reason_code, properties):
        general_logger.warn("Disconnected result code: " + str(reason_code))

    client_id = f"wudsPi-{random.randint(0, 1000)}"
    # Set Connecting Client ID
    client = mqtt_client.Client(
        paho_enums.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt_client.MQTTv5
    )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Set LWT for client if it goes down
    client.will_set(status_topic, payload="Offline", qos=1, retain=True)
    client.connect(broker, port, 60, clean_start=False)

    client.loop_start()
    client.publish(status_topic, "Online", qos=1, retain=True)
    general_logger.info("Client connected flag: " + str(client.is_connected()))
    return client


# Rotating logger and data formatting based on packet type
def probe_log_build(C: mqtt_client, logger: logging):

    def probe_handler(packet):
        radio = str(packet.mysummary)
        log_time = time.get_log_time()

        MAC = str(packet.addr2).upper()
        clientOUI = MAC[:8]
        firstOctet = clientOUI[:2]
        binaryRep = probes.binaryrep(firstOctet)

        # We're only concerned with wifi probes, i.e. packets with Dot11ProbeReq layer
        if packet.haslayer(Dot11ProbeReq):
            # print(packet.info)
            # print(packet.info.decode("utf-8", "ignore"))
            # print(packet.info.decode("utf-16", "ignore"))
            # Handle known devices: if *full MAC address* is included it was added from knownlist.json
            if OUIMEM.get(MAC.lower()):
                # Noisy to actually log this but uncomment to debug
                # general_logger.info(f"{OUIMEM.get(MAC.lower())} seen")
                pass
            else:
                probe = [
                    log_time,
                    probes.rssi(radio),
                    probes.channel(radio),
                    MAC.lower(),
                ]
                if OUIMEM.get(clientOUI) is not None:
                    probe.append(OUIMEM.get(clientOUI))
                else:
                    if binaryRep[6:7] == "1":
                        probe.append("Locally Assigned")
                    else:
                        probe.append("Unknown OUI")
                try:
                    if "\x00" not in packet[Dot11ProbeReq].info.decode(
                        "utf-8", "ignore"
                    ):
                        if str(packet.info):
                            decoded = str(packet.info.decode("utf-8", "ignore"))
                            BSSID = decoded if decoded != "" else "Undirected Probe"
                            probe.append(BSSID)
                except UnicodeDecodeError:
                    general_logger.error(
                        "Unicode decode error: ",
                        packet[Dot11ProbeReq].info.decode("utf-8", "ignore"),
                    )
                # Logger writes probe to local CSV file (and STDOUT)
                logger.info(CSVDelim.join(probe))
                # MQQT Client publishes json-encoded data to broker
                C.publish(topic, probe_json(probe))

    return probe_handler


def main():
    # Arguments for terminal control
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--monitor")
    parser.add_argument("-f", "--file")
    args = parser.parse_args()

    if not args.monitor:
        print("Monitor mode adapter not set with -m flag")
        sys.exit(-1)

    if not args.file:
        print("Output location not set with -f flag")
        sys.exit(-1)

    general_logger.info("**** Sniff script started ****")
    logger = logging.getLogger("PROBES")
    # Output location
    handler = RotatingFileHandler(str(args.file) + ".csv")
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    build_oui_lookup()

    C = connect_mqtt()
    while True:
        if C.is_connected() == False:
            general_logger("Detected client disconnect, reconnecting now")
            C = connect_mqtt()
            time.sleep(5)
        try:
            sniff(iface=args.monitor, prn=probe_log_build(C, logger), store=0)
        except Exception as e:
            general_logger.warning(type(e))
            general_logger.error(e)


if __name__ == "__main__":
    main()
