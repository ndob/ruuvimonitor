import os
os.environ["RUUVI_BLE_ADAPTER"] = "bleak"

import argparse
import asyncio
import datetime
import sqlite3
import traceback

async def collect(update_interval, db):
    from ruuvitag_sensor.ruuvi import RuuviTagSensor
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
                db.cursor().execute('''INSERT INTO reading(
                    mac,
                    temperature,
                    humidity,
                    pressure,
                    acceleration,
                    acceleration_x,
                    acceleration_y,
                    acceleration_z,
                    tx_power,
                    battery,
                    movement_counter,
                    measurement_sequence_number,
                    rssi,
                    data_format
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    [
                        data[1]["mac"],
                        data[1]["temperature"],
                        data[1]["humidity"],
                        data[1]["pressure"],
                        data[1]["acceleration"],
                        data[1]["acceleration_x"],
                        data[1]["acceleration_y"],
                        data[1]["acceleration_z"],
                        data[1]["tx_power"],
                        data[1]["battery"],
                        data[1]["movement_counter"],
                        data[1]["measurement_sequence_number"],
                        data[1]["rssi"],
                        data[1]["data_format"]
                    ])
                db.commit()
                last_update[mac_address] = datetime.datetime.now()
                break
            except:
                print(traceback.format_exc())
                print(f"Insert failed. Retrying... Retry number: {i}.")

def run_collector(db_filename, update_interval):
    print(f"Collector starting with update interval: {update_interval}")
    db = sqlite3.connect(db_filename, timeout=10)
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)
    asyncio.get_event_loop().run_until_complete(collect(update_interval, db))
