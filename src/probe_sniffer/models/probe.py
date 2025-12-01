import json
from probe_sniffer.storage.dto import SightingDTO


class Probe:
    """
    Class to hold some formatting logic for a wifi probe
    """

    def __init__(
        self,
        timestamp: str,
        dBm: int,
        channel: int,
        mac: str,
        oui="Unknown OUI",
        ssid="Undirected Probe",
        device_name="",
    ) -> None:
        self.timestamp = timestamp
        self.dBm = dBm
        self.channel = channel
        self.mac = mac
        self.oui = oui
        self.ssid = ssid
        self.device_name = device_name

    def mqtt_json(self) -> json:
        """
        Returns json object to be published to mqtt topic
        """
        return json.dumps(
            {
                "timestamp": self.timestamp,
                "rssi": self.dBm,
                "channel": self.channel,
                "MAC": self.mac,
                "clientOUI": self.oui,
                "SSID": self.ssid,
            }
        )

    def to_csv(self) -> str:
        """Returns csv string for logging
        024-04-04 14:00:26,-77dBm,8,e2:1d:5e:17:3f:0d,Locally Assigned,Red Sox-2.4
        """
        return ",".join(
            [
                self.timestamp,
                str(self.dBm) + " dBm",
                "Ch: " + str(self.channel),
                self.mac,
                self.oui,
                self.ssid,
            ]
        )

    def to_supabase(self) -> str:
        return {
            "timestamp": self.timestamp,
            "mac": self.mac,
            "name": self.device_name,
            "rssi": self.dBm,
            "oui": self.oui,
            "ssid": self.ssid,
        }

    def to_sighting_dto(self) -> SightingDTO:
        """
        Convert Probe to SightingDTO for storage layer.

        Returns:
            SightingDTO object for database persistence
        """
        return SightingDTO(
            mac=self.mac,
            dbm=self.dBm,
            ssid=self.ssid,
            oui=self.oui,
        )
