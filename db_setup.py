# db_setup.py (optional script or part of app.py)
import sqlite3

conn = sqlite3.connect('parking.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT UNIQUE NOT NULL,
    vehicle_type TEXT,
    owner_name TEXT,
    phone_number TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_type TEXT,
    is_occupied INTEGER DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS parking_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    slot_id INTEGER,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME,
    total_fee REAL,
    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY(slot_id) REFERENCES parking_slots(slot_id)
)''')

# Initialize a few slots
c.executemany("INSERT INTO parking_slots (slot_type) VALUES (?)", [('Car',), ('Car',), ('Bike',), ('Bike',)])
conn.commit()
conn.close()
