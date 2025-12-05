# Holds all probe-handling utils

import hashlib
import json
from scapy.layers.dot11 import Dot11Elt


def rssi(radiodata) -> str:
    """
    Finds signal strength of probe
    """
    if "dBm_AntSignal=" in radiodata:
        start = radiodata.find("dBm_AntSignal=")
        return str(radiodata[start + 14 : start + 21]).replace(" ", "").replace("A", "")
    else:
        return "-255dBm"


def get_dBm(radiodata: str) -> int:
    """
    Finds signal strength in dBm
    """
    start_index = radiodata.find("dBm_AntSignal=")
    if start_index != -1:
        # Extract the substring after "dBm_AntSignal="
        substring = radiodata[start_index + len("dBm_AntSignal=") :]

        # Find the end of the integer value
        end_index = substring.find(" ")

        # Extract the integer value
        if end_index != -1:
            dbm_antsignal = int(substring[:end_index])
            return dbm_antsignal
        else:
            # If no space is found, the integer value continues till the end of the string
            dbm_antsignal = int(substring)
            return dbm_antsignal
    else:
        return -255


def channel_frequency(radiodata) -> str:
    """
    Find Wifi channel number and signal frequency
    e.g.: C:04 2427Mhz
    """
    if "ChannelFrequency=" in radiodata:
        data = radiodata
        start = data.find("ChannelFrequency=")
        channelNumber = data[start + 17 : start + 21]
        freq = int(channelNumber)

        if freq == 2412:
            return "C:01 " + str(freq) + "Mhz"
        if freq == 2417:
            return "C:02 " + str(freq) + "Mhz"
        if freq == 2422:
            return "C:03 " + str(freq) + "Mhz"
        if freq == 2427:
            return "C:04 " + str(freq) + "Mhz"
        if freq == 2432:
            return "C:05 " + str(freq) + "Mhz"
        if freq == 2437:
            return "C:06 " + str(freq) + "Mhz"
        if freq == 2442:
            return "C:07 " + str(freq) + "Mhz"
        if freq == 2447:
            return "C:08 " + str(freq) + "Mhz"
        if freq == 2452:
            return "C:09 " + str(freq) + "Mhz"
        if freq == 2457:
            return "C:10 " + str(freq) + "Mhz"
        if freq == 2462:
            return "C:11 " + str(freq) + "Mhz"
        if freq == 2467:
            return "C:12 " + str(freq) + "Mhz"
        if freq == 2472:
            return "C:13 " + str(freq) + "Mhz"
        if freq == 2484:
            return "C:14 " + str(freq) + "Mhz"
        else:
            return "-->>" + str(freq)
    return "Channel unknown"


def get_channel_number(radiodata) -> int:
    freq_str = channel_frequency(radiodata)
    # split str into first 2 chars and coerce to integer
    colon_index = freq_str.find(":")
    if colon_index != -1:
        # Extract the channel substring after ":"
        substring = freq_str[colon_index + 1 : 4]

        # Extract the numeric part from the substring
        numeric_part = "".join(filter(str.isdigit, substring))

        # Convert the numeric part to an integer
        result = int(numeric_part)

        return result
    else:
        return 0


def binaryrep(firstOctet, scale=16, num_of_bits=8):
    """
    Reads first octet of a MAC address as binary and returns it as a string.
    Will return None if the probe contains a "NONE" mac address
    """
    # Handle "NONE" MAC Addresses
    if firstOctet == "NO":
        return
    integer = int(firstOctet, scale)
    binary = bin(integer)
    return str(binary[2:].zfill(num_of_bits))


def extract_ie_fingerprint(packet) -> tuple[str, list[dict] | None]:
    """
    Extract Information Elements from a probe request packet and generate fingerprint.

    Excludes variable IEs that change frequently:
      - IE 0 (SSID) - varies per network
      - IE 3 (DS Parameter Set / Channel) - varies per channel
      - IE 221 (Vendor Specific) - contains timestamps/counters not useful for fingerprinting

    Args:
        packet: Scapy Dot11ProbeReq packet

    Returns:
        Tuple of (fingerprint_hash, ie_data_json) where:
          - fingerprint_hash: 16-char hex string
          - ie_data_json: List of IE dicts for storage (None if no IEs found)
    """

    # IEs to exclude from fingerprint (too variable)
    EXCLUDE_IES = {0, 3, 221}

    ie_list = []
    ie_raw = []

    # Iterate through all Dot11Elt layers
    dot11elt = packet.getlayer(Dot11Elt)
    while dot11elt:
        ie_id = dot11elt.ID
        ie_len = dot11elt.len if hasattr(dot11elt, "len") else 0
        ie_info = bytes(dot11elt.info) if dot11elt.info else b""

        # Store full IE data for debugging
        ie_list.append(
            {
                "id": ie_id,
                "len": ie_len,
                "data": ie_info.hex(),
            }
        )

        # Store raw IE for fingerprinting (ID:length:data)
        # Only include stable IEs in fingerprint calculation
        if ie_id not in EXCLUDE_IES:
            ie_raw.append(f"{ie_id}:{ie_len}:{ie_info.hex()}")

        # Move to next IE
        dot11elt = dot11elt.payload.getlayer(Dot11Elt)

    # Generate fingerprint from stable IEs
    if not ie_raw:
        return ("no_stable_ies", None)

    # Sort for consistency, hash, truncate to 16 chars
    fingerprint_data = "|".join(sorted(ie_raw))
    fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

    # Return fingerprint and full IE data (for storage)
    return (fingerprint, ie_list if ie_list else None)
