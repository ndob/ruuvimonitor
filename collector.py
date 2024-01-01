import os
os.environ["RUUVI_BLE_ADAPTER"] = "bleak"

import argparse
import asyncio
import datetime
import sqlite3
import traceback
from ruuvitag_sensor.ruuvi import RuuviTagSensor

DATABASE_NAME = "readings.db"
db = sqlite3.connect(DATABASE_NAME, timeout=10)

# Add: all fields, index for mac
def create_db():
    # db.cursor().execute('''PRAGMA synchronous = EXTRA''')
    # Makes inserts much faster and in this use case ok.
    db.cursor().execute('''PRAGMA journal_mode = WAL''')
    # Add version so we can create proper schema migration going forward.
    db.cursor().execute('''PRAGMA user_version = 1''')
    db.cursor().execute('''CREATE TABLE IF NOT EXISTS reading(
        mac TEXT,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
    )''')
    db.cursor().execute('''CREATE TABLE IF NOT EXISTS sensor_metadata(
        mac TEXT UNIQUE,
        name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
    )''')
    db.cursor().execute('''CREATE TABLE IF NOT EXISTS reading_newest(
        mac TEXT UNIQUE,
        reading_id INTEGER,
        FOREIGN KEY(reading_id) REFERENCES reading(rowid));
    ''')
    db.cursor().execute('''CREATE TRIGGER IF NOT EXISTS trigger_update_newest_readings AFTER INSERT ON reading 
        BEGIN
            INSERT INTO reading_newest (mac, reading_id) VALUES (NEW.mac, NEW.rowid) ON CONFLICT(mac) DO UPDATE SET reading_id=NEW.rowid;
        END;
    ''')

    #db.cursor().execute('''CREATE INDEX IF NOT EXISTS idx_reading_mac ON reading(mac)''')
    #db.cursor().execute('''CREATE INDEX IF NOT EXISTS idx_reading_timestamp ON reading(timestamp DESC)''')
    #db.cursor().execute('''CREATE INDEX IF NOT EXISTS idx_reading_mactimestamp ON reading(mac, timestamp DESC)''')
    #db.cursor().execute('''CREATE INDEX IF NOT EXISTS idx_reading_timestampmac ON reading(timestamp DESC, mac)''')
    db.cursor().execute('''CREATE INDEX IF NOT EXISTS idx_reading_date ON reading(DATE(timestamp))''')

async def main(update_interval):
    last_update = dict()
    async for data in RuuviTagSensor.get_data_async():
        mac_address = data[1]["mac"]
        if mac_address in last_update.keys() and (datetime.datetime.now() - last_update[mac_address]).total_seconds() < update_interval:
            print(f"Skipping update for {mac_address} - {(datetime.datetime.now() - last_update[mac_address]).total_seconds()}")
            continue

        # 10 retries
        for i in range(10):
            try:
                print(data)
                db.cursor().execute("INSERT INTO reading(mac, temperature, humidity, pressure) VALUES(?, ?, ?, ?)", [data[1]["mac"], data[1]["temperature"], data[1]["humidity"], data[1]["pressure"]])
                db.commit()
                last_update[mac_address] = datetime.datetime.now()
                break
            except:
                print(traceback.format_exc())
                print(f"Insert failed. Retrying... Retry number: {i}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--update-interval", type=int, default=60, help="Interval in seconds for sensor reading updates.")
    args = parser.parse_args()

    create_db()
    asyncio.get_event_loop().run_until_complete(main(args.update_interval))
