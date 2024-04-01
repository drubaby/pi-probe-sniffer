import os
import json
from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()


def create_supabase_client() -> Client:
    """Create client with .env values"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")
    supabase: Client = create_client(url, key)
    return supabase


def get_trusted_devices(supabase: Client) -> str:
    """
    Returns a list of
    """
    data = (
        supabase.table("known_devices")
        .select("mac", "name")
        .eq("is_trusted", True)
        .execute()
    )
    return json.dumps(data.data)
