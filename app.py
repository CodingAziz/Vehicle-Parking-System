from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__) # Initialise Flask App
app.secret_key = "supersecretkey"
DB = "parking.db" 


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row # Create the db row
    return conn


def reset_database():
    """Drops all tables and recreates them for a clean state each refresh."""
    conn = get_db()
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS parking_records")
    c.execute("DROP TABLE IF EXISTS vehicles")
    c.execute("DROP TABLE IF EXISTS parking_slots")

    c.execute("""
    CREATE TABLE vehicles (
        vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_number TEXT UNIQUE NOT NULL,
        vehicle_type TEXT NOT NULL,
        owner_name TEXT NOT NULL,
        phone_number TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE parking_slots (
        slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_type TEXT NOT NULL,
        is_occupied INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE parking_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        slot_id INTEGER NOT NULL,
        entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        exit_time DATETIME,
        total_fee REAL,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(vehicle_id),
        FOREIGN KEY(slot_id) REFERENCES parking_slots(slot_id)
    )
    """)

    slots = [('Car',), ('Car',), ('Car',), ('Bike',), ('Bike',), ('Truck',)]
    c.executemany("INSERT INTO parking_slots (slot_type) VALUES (?)", slots)
    conn.commit()
    conn.close()


# Initialize DB once at server startup if file does not exist
if not os.path.exists(DB):
    reset_database()
else:
    print("Existing database found, skipping reset.")


@app.route('/')
def index():
    conn = get_db() 
    vehicles = conn.execute("SELECT * FROM vehicles").fetchall()
    parked = conn.execute("""
        SELECT pr.*, v.plate_number, ps.slot_type 
        FROM parking_records pr
        JOIN vehicles v ON pr.vehicle_id = v.vehicle_id
        JOIN parking_slots ps ON pr.slot_id = ps.slot_id
        WHERE pr.exit_time IS NULL
    """).fetchall()
    conn.close()
    return render_template('index.html', vehicles=vehicles, parked=parked)


@app.route('/add_vehicle', methods=['GET', 'POST'])
def add_vehicle():
    if request.method == 'POST':
        plate_number = request.form.get('plate_number', '').strip()
        vehicle_type = request.form.get('vehicle_type', '').strip()
        owner_name = request.form.get('owner_name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        if not all([plate_number, vehicle_type, owner_name, phone_number]):
            flash("All fields are required.", "error")
            return redirect(url_for('add_vehicle'))

        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO vehicles (plate_number, vehicle_type, owner_name, phone_number)
                VALUES (?, ?, ?, ?)
            """, (plate_number, vehicle_type, owner_name, phone_number))
            conn.commit()
            flash("Vehicle added successfully.", "success")
        except sqlite3.IntegrityError:
            flash("Vehicle with this plate number already exists.", "error")
        finally:
            conn.close()
        return redirect(url_for('index'))

    return render_template('add_vehicle.html')


@app.route('/park_vehicle', methods=['GET', 'POST'])
def park_vehicle():
    conn = get_db()
    vehicles = conn.execute("SELECT * FROM vehicles").fetchall()
    slots = conn.execute("SELECT * FROM parking_slots WHERE is_occupied = 0").fetchall()

    if request.method == 'POST':
        vehicle_id = request.form.get('vehicle_id')
        slot_id = request.form.get('slot_id')

        if not vehicle_id or not slot_id:
            flash("Select both vehicle and slot.", "error")
            return redirect(url_for('park_vehicle'))

        conn.execute("INSERT INTO parking_records (vehicle_id, slot_id) VALUES (?, ?)", (vehicle_id, slot_id))
        conn.execute("UPDATE parking_slots SET is_occupied = 1 WHERE slot_id = ?", (slot_id,))
        conn.commit()
        conn.close()
        flash("Vehicle parked successfully.", "success")
        return redirect(url_for('index'))

    conn.close()
    return render_template('park_vehicle.html', vehicles=vehicles, slots=slots)


@app.route('/exit_vehicle/<int:record_id>')
def exit_vehicle(record_id):
    conn = get_db()
    record = conn.execute("""
        SELECT pr.*, v.vehicle_type, ps.slot_type
        FROM parking_records pr
        JOIN vehicles v ON pr.vehicle_id = v.vehicle_id
        JOIN parking_slots ps ON pr.slot_id = ps.slot_id
        WHERE pr.record_id = ?
    """, (record_id,)).fetchone()
    if record:
      entry_time = datetime.fromisoformat(record['entry_time'])
      hours = max((datetime.now() - entry_time).total_seconds() / 3600, 1)

      RATE = {"Car": 20, "Bike": 10, "Truck": 30}
      hourly_rate = RATE.get(record['vehicle_type'], 20)
      fee = round(hours * hourly_rate, 2)

      conn.execute("""
          UPDATE parking_records 
          SET exit_time = CURRENT_TIMESTAMP, total_fee = ?
          WHERE record_id = ?
      """, (fee, record_id))

      conn.execute("UPDATE parking_slots SET is_occupied = 0 WHERE slot_id = ?", (record['slot_id'],))
      conn.commit()
      flash(f"Vehicle exited. Fee: ₹{fee}", "info")
    conn.close()
    return redirect(url_for('index'))


@app.route('/revenue')
def revenue():
    conn = get_db()
    records = conn.execute("""
    SELECT pr.*, v.plate_number, v.vehicle_type, ps.slot_type
    FROM parking_records pr
    JOIN vehicles v ON pr.vehicle_id = v.vehicle_id
    JOIN parking_slots ps ON pr.slot_id = ps.slot_id
    """).fetchall()
    conn.close()

    RATE = {
    "Car": 20,
    "Bike": 10,
    "Truck": 30
    }

    data = []
    total_revenue = 0

    for r in records:
        entry = datetime.fromisoformat(r["entry_time"])
        exit_time = datetime.fromisoformat(r["exit_time"]) if r["exit_time"] else datetime.now()
        hours = (exit_time - entry).total_seconds() / 3600

        # use joined vehicle_type to pick correct rate
        hourly_rate = RATE.get(r["vehicle_type"], 20)
        fee = round(hours * hourly_rate, 2)

        data.append({
            "plate": r["plate_number"],
            "type": r["vehicle_type"],
            "entry": r["entry_time"],
            "exit": r["exit_time"] or "Still Parked",
            "fee": fee
        })
        total_revenue += fee

    return render_template("revenue.html", data=data, total_revenue=round(total_revenue, 2))


if __name__ == '__main__':
    app.run(debug=True)
