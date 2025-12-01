"""Database schema for local SQLite database."""

SCHEMA = """
-- Devices table: tracks all WiFi devices (trusted and untrusted)
CREATE TABLE IF NOT EXISTS devices (
    mac TEXT PRIMARY KEY,
    name TEXT,
    is_trusted INTEGER DEFAULT 0,  -- SQLite uses INTEGER for boolean
    first_seen TEXT NOT NULL,      -- ISO 8601: 'YYYY-MM-DD HH:MM:SS'
    last_seen TEXT NOT NULL        -- ISO 8601: 'YYYY-MM-DD HH:MM:SS'
);

-- Sightings table: logs each probe request capture
CREATE TABLE IF NOT EXISTS sightings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,       -- ISO 8601: 'YYYY-MM-DD HH:MM:SS'
    mac TEXT NOT NULL,
    rssi TEXT,                     -- Signal strength string (e.g., "-75dBm")
    dbm INTEGER,                   -- Signal strength as integer
    ssid TEXT,                     -- Probed SSID or "Undirected Probe"
    oui TEXT,                      -- Manufacturer/OUI designation
    FOREIGN KEY (mac) REFERENCES devices(mac)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_sightings_timestamp
    ON sightings(timestamp);

CREATE INDEX IF NOT EXISTS idx_sightings_mac
    ON sightings(mac);

CREATE INDEX IF NOT EXISTS idx_devices_trusted
    ON devices(is_trusted);
"""
