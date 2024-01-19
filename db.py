import sqlite3

def create_db(db):
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

def migrate1to2(db):
    db.cursor().execute('''ALTER TABLE reading ADD acceleration REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD acceleration_x REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD acceleration_y REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD acceleration_z REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD tx_power REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD battery REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD movement_counter INTEGER''')
    db.cursor().execute('''ALTER TABLE reading ADD measurement_sequence_number INTEGER''')
    db.cursor().execute('''ALTER TABLE reading ADD rssi REAL''')
    db.cursor().execute('''ALTER TABLE reading ADD data_format INTEGER''')

    db.cursor().execute('''PRAGMA user_version = 2''')

def migrate2to3(db):
    db.cursor().execute('''CREATE INDEX IF NOT EXISTS idx_reading_datetime ON reading(DATETIME(timestamp))''')
    db.cursor().execute('''PRAGMA user_version = 3''')

def init_db(db_filename):
    db = sqlite3.connect(db_filename, timeout=10)

    while True:
        db_version = db.cursor().execute("pragma user_version").fetchone()
        if not db_version:
            print("No version info found. Bailing out.")
            break

        version = db_version[0]
        print(f"Current DB version: {version}")

        if version == 0:
            print("Creating DB.")
            create_db(db)
        elif version == 1:
            print("Migrating to version 2.")
            migrate1to2(db)
        elif version == 2:
            print("Migrating to version 3.")
            migrate2to3(db)
        else:
            break

    print("DB init done.")
