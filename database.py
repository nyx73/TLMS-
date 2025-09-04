import sqlite3
import os
from datetime import datetime
import random # Import random for dummy data generation
import traffic_data # Import traffic_data to get AREA information and generate vehicle numbers/types

DATABASE_FILE = 'traffic_data.db'

def init_db():
    """Initializes the SQLite database and creates the necessary tables."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Create traffic_logs table to store historical traffic data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_name TEXT NOT NULL,
            lane_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            two_wheelers INTEGER,
            four_wheelers INTEGER,
            density INTEGER
        )
    ''')

    # Create alert_thresholds table to store customizable alert settings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_thresholds (
            area_name TEXT PRIMARY KEY,
            max_density INTEGER NOT NULL DEFAULT 150
        )
    ''')

    # Create challans table to store violation records
    # Added owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_name TEXT NOT NULL,
            lane_id TEXT,
            violation_type TEXT NOT NULL,
            vehicle_number TEXT,
            owner_name TEXT,
            owner_phone TEXT,
            vehicle_type TEXT,
            challan_number TEXT,
            transaction_id TEXT,
            state TEXT,
            fine_amount INTEGER,    -- New column
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending' -- 'pending', 'paid', 'disputed'
        )
    ''')

    conn.commit()

    # Check if challans table is empty and pre-populate if it is
    cursor.execute("SELECT COUNT(*) FROM challans")
    if cursor.fetchone()[0] == 0:
        _add_initial_dummy_challans(conn)

    conn.close()
    print(f"Database '{DATABASE_FILE}' initialized successfully.")

def _add_initial_dummy_challans(conn):
    """
    Adds initial dummy challan data for each area if the challans table is empty.
    This ensures there's always some data to display.
    """
    cursor = conn.cursor()
    print("Populating initial dummy challans...")

    for area_name, lanes in traffic_data.AREAS.items():
        # Add at least two challans per area
        for i in range(2):
            lane_id = random.choice(lanes)
            violation_type = random.choice(traffic_data.VIOLATION_TYPES)
            
            # Try to get a dummy person from the list
            person_data = random.choice(traffic_data.DUMMY_PEOPLE_VEHICLES)
            vehicle_number = person_data['rc_number']
            owner_name = person_data['name']
            owner_phone = person_data['phone']
            vehicle_type = person_data['vehicle_type']
            
            challan_number = traffic_data.generate_challan_number()
            transaction_id = traffic_data.generate_transaction_id()
            state = traffic_data.get_state_from_rc(vehicle_number)
            fine_amount = traffic_data.FINE_AMOUNTS.get(violation_type, 200) # Get fine amount

            timestamp = datetime.now().isoformat()
            status = 'pending' if i == 0 else random.choice(['pending', 'paid']) # Make one pending, one random

            cursor.execute('''
                INSERT INTO challans (area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount, timestamp, status))
    conn.commit()
    print("Initial dummy challans added.")


def log_traffic_data(area_name, lanes_info):
    """Logs current traffic data for all lanes in a given area to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()

    for lane_id, data in lanes_info.items():
        cursor.execute('''
            INSERT INTO traffic_logs (area_name, lane_id, timestamp, two_wheelers, four_wheelers, density)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (area_name, lane_id, timestamp, data['two_wheelers'], data['four_wheelers'], data['density']))

    conn.commit()
    conn.close()

def get_historical_traffic_data(area_name, lane_id=None, limit=100):
    """
    Fetches historical traffic density data for a given area and optionally a specific lane.
    Returns data ordered by timestamp, limited by 'limit'.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    query = "SELECT timestamp, density FROM traffic_logs WHERE area_name = ?"
    params = [area_name]

    if lane_id:
        query += " AND lane_id = ?"
        params.append(lane_id)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    # Reverse the data to get chronological order for charting
    return data[::-1]

def get_alert_threshold(area_name):
    """Retrieves the alert density threshold for a specific area."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT max_density FROM alert_thresholds WHERE area_name = ?", (area_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 150 # Default to 150 if not set

def set_alert_threshold(area_name, max_density):
    """Sets or updates the alert density threshold for a specific area."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO alert_thresholds (area_name, max_density)
        VALUES (?, ?)
    ''', (area_name, max_density))
    conn.commit()
    conn.close()

def add_challan(area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount):
    """Adds a new challan record to the database with all details."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO challans (area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount, timestamp, 'pending'))
    conn.commit()
    challan_id = cursor.lastrowid
    conn.close()
    return challan_id

def get_challans(area_name, status=None):
    """Fetches challan records for a given area, optionally filtered by status."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Updated SELECT statement to include new columns
    query = "SELECT id, area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount, timestamp, status FROM challans WHERE area_name = ?"
    params = [area_name]

    if status and status != 'all':
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY timestamp DESC"
    cursor.execute(query, params)
    challans = cursor.fetchall()
    conn.close()
    # Convert to list of dictionaries for easier JSON serialization
    challan_list = []
    for c in challans:
        challan_list.append({
            'id': c[0],
            'area_name': c[1],
            'lane_id': c[2],
            'violation_type': c[3],
            'vehicle_number': c[4],
            'owner_name': c[5],
            'owner_phone': c[6],
            'vehicle_type': c[7],
            'challan_number': c[8],
            'transaction_id': c[9],
            'state': c[10],
            'fine_amount': c[11],    # New field
            'timestamp': c[12],
            'status': c[13]
        })
    return challan_list

def get_challan_by_id(challan_id):
    """Fetches a single challan record by its ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    # Updated SELECT statement to include new columns
    query = "SELECT id, area_name, lane_id, violation_type, vehicle_number, owner_name, owner_phone, vehicle_type, challan_number, transaction_id, state, fine_amount, timestamp, status FROM challans WHERE id = ?"
    cursor.execute(query, (challan_id,))
    c = cursor.fetchone()
    conn.close()
    if c:
        return {
            'id': c[0],
            'area_name': c[1],
            'lane_id': c[2],
            'violation_type': c[3],
            'vehicle_number': c[4],
            'owner_name': c[5],
            'owner_phone': c[6],
            'vehicle_type': c[7],
            'challan_number': c[8],
            'transaction_id': c[9],
            'state': c[10],
            'fine_amount': c[11],
            'timestamp': c[12],
            'status': c[13]
        }
    return None

def update_challan_status(challan_id, new_status):
    """Updates the status of a specific challan."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE challans SET status = ? WHERE id = ?", (new_status, challan_id))
    conn.commit()
    conn.close()
    return True

if __name__ == '__main__':
    # Example usage for testing database functions
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE) # Clean up for fresh test

    init_db()

    # Simulate some initial data and log it
    test_area = "Sayajigunj"
    # Note: simulate_traffic_data now returns a tuple (lanes_data, violation_details)
    # We only need lanes_data for logging traffic, so we unpack it.
    from traffic_data import simulate_traffic_data
    for _ in range(5):
        sim_data, _ = simulate_traffic_data(test_area)
        if sim_data:
            log_traffic_data(test_area, sim_data)
            print(f"Logged data for {test_area}")
            time.sleep(0.5)

    # Test adding challans with new fields
    print("\nAdding some sample challans (beyond initial dummy data):")
    add_challan(test_area, "Lane 1", "Red Light Violation", "GJ06AB1234", "Aarav Sharma", "9876543210", "Motorcycle", "CHLN-2024-000001", "TXN-ABC123DEF456", "GJ", 500)
    add_challan(test_area, "Lane 2", "No Helmet", "GJ06CD5678", "Aditi Patel", "9988776655", "Car", "CHLN-2024-000002", "TXN-GHI789JKL012", "GJ", 200)
    update_challan_status(1, 'paid') # Mark first challan as paid
    add_challan("Akota Bridge", "Lane A", "Over Speeding", "GJ06EF9012", "Vivaan Singh", "9123456789", "Motorcycle", "CHLN-2024-000003", "TXN-MNO345PQR678", "GJ", 1500)

    # Test fetching challans
    print("\nChallans for Sayajigunj (all):")
    challans_sayajigunj = get_challans(test_area)
    for c in challans_sayajigunj:
        print(c)

    print("\nChallans for Sayajigunj (pending):")
    challans_pending = get_challans(test_area, status='pending')
    for c in challans_pending:
        print(c)

    print("\nSetting and getting alert threshold for Sayajigunj:")
    set_alert_threshold(test_area, 200)
    threshold = get_alert_threshold(test_area)
    print(f"Threshold for {test_area}: {threshold}")
