# 🅿️ Vehicle Parking System – Database Setup

This script (`db_setup.py`) creates and initializes the SQLite database used by the Vehicle Parking Management System.

---

## ⚙️ Purpose

The main goal of `db_setup.py` is to:
- Create the **parking.db** database file.
- Define all required tables.
- Insert a few initial parking slots for use in the application.

---

## 🧱 Database Tables

### 1. `vehicles`
Stores information about registered vehicles.

| Column | Description |
|---------|-------------|
| `vehicle_id` | Unique ID for each vehicle |
| `plate_number` | Vehicle’s registration number |
| `vehicle_type` | Type of vehicle (Car/Bike) |
| `owner_name` | Owner’s name |
| `phone_number` | Owner’s contact number |

---

### 2. `parking_slots`
Keeps track of available parking slots.

| Column | Description |
|---------|-------------|
| `slot_id` | Unique ID for each slot |
| `slot_type` | Slot type (Car/Bike) |
| `is_occupied` | 0 → Free, 1 → Occupied |

---

### 3. `parking_records`
Logs each parking event for a vehicle.

| Column | Description |
|---------|-------------|
| `record_id` | Unique record ID |
| `vehicle_id` | References a vehicle |
| `slot_id` | References a parking slot |
| `entry_time` | Time vehicle entered |
| `exit_time` | Time vehicle exited |
| `total_fee` | Calculated parking fee |

---

## 🏗️ How It Works

1. Connects to SQLite (`parking.db`)
2. Creates the three tables if they don’t exist
3. Adds default slots (2 Car slots, 2 Bike slots)
4. Saves and closes the database connection

---

## ▶️ How to Run

```bash
python db_setup.py
