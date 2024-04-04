import os
import json
import sys
from supabase import Client, create_client
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import Probe

load_dotenv()


def create_supabase_client() -> Client:
    """Create client with .env values"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")
    supabase: Client = create_client(url, key)
    return supabase


def get_trusted_devices(supabase: Client) -> str:
    """
    Returns a json list of devices that have been marked Trusted
    """
    data = (
        supabase.table("known_devices")
        .select("mac", "name")
        .eq("is_trusted", True)
        .execute()
    )
    return json.dumps(data.data)


def log_sighting(supabase: Client, probe: Probe):
    """
    Logs probes to the device_sightings table in supabase db

    timestamp
    mac
    name
    rssi
    oui
    ssid

    """

    # timestamp
    # print("sending to db: ", probe.to_supabase())

    data = supabase.table("device_sightings").insert(probe.to_supabase()).execute()
    return data
