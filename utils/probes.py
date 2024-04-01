# Holds all probe-handling utils


def rssi(radiodata) -> str:
    """
    Finds signal strength of probe
    """
    if "dBm_AntSignal=" in radiodata:
        start = radiodata.find("dBm_AntSignal=")
        return str(radiodata[start + 14 : start + 21]).replace(" ", "").replace("A", "")
    else:
        return "-255dBm"


def channel(radiodata) -> str:
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
