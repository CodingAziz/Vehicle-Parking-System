# db_setup.py (optional script or part of app.py)
import sqlite3

conn = sqlite3.connect('parking.db')
c = conn.cursor()


# Users table with first name, last name, email
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
)''')

# Vehicles table linked to user_id, plate_number unique per user
c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT NOT NULL,
    vehicle_type TEXT,
    owner_name TEXT,
    phone_number TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    UNIQUE(plate_number, user_id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_type TEXT,
    is_occupied INTEGER DEFAULT 0
)''')


# Parking records linked to user_id
c.execute('''CREATE TABLE IF NOT EXISTS parking_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER,
    slot_id INTEGER,
    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME,
    total_fee REAL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id),
    FOREIGN KEY(slot_id) REFERENCES parking_slots(slot_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)''')

slots = [('Car',)] * 10 + [('Truck',)] * 5 + [('Bike',)] * 8
c.executemany("INSERT INTO parking_slots (slot_type) VALUES (?)", slots)
conn.commit()
conn.close()
