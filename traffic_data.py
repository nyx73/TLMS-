import random
import time
from datetime import datetime

# Predefined areas/intersections with their lane configurations
# These are common residential areas in Vadodara, chosen to represent different traffic points.
AREAS = {
    "Sayajigunj": ["Lane 1", "Lane 2", "Lane 3", "Lane 4"],
    "Akota Bridge": ["Lane A", "Lane B", "Lane C", "Lane D"],
    "Race Course": ["North Lane", "South Lane", "East Lane", "West Lane"],
    "Dabhoi Road": ["Lane X", "Lane Y", "Lane Z", "Lane W"],
    "Alkapuri": ["Road 1", "Road 2", "Road 3", "Road 4"],
    "Gotri Road": ["Intersection A", "Intersection B", "Intersection C", "Intersection D"],
    "Manjalpur": ["Sector N", "Sector S", "Sector E", "Sector W"],
    "Karelibaug": ["Main Rd North", "Main Rd South", "Cross Rd East", "Cross Rd West"],
    "Vasna-Bhayli Road": ["Entry Point", "Exit Point", "Bypass Lane 1", "Bypass Lane 2"],
    "Waghodia Road": ["Junction 1", "Junction 2", "Junction 3", "Junction 4"],
    "Sama-Savli Road": ["Route P", "Route Q", "Route R", "Route S"],
    "Old Padra Road": ["Segment Alpha", "Segment Beta", "Segment Gamma", "Segment Delta"]
}

# List of possible violation types (for simulation)
VIOLATION_TYPES = [
    "Red Light Violation",
    "No Helmet",
    "Triple Riding",
    "Wrong Side Driving",
    "No Seatbelt",
    "Using Mobile While Driving",
    "Parking Violation",
    "Over Speeding",
    "Signal Jumping"
]

# Fine amounts for different violation types
FINE_AMOUNTS = {
    "Red Light Violation": 500,
    "No Helmet": 200,
    "Triple Riding": 300,
    "Wrong Side Driving": 750,
    "No Seatbelt": 500,
    "Using Mobile While Driving": 1000,
    "Parking Violation": 100,
    "Over Speeding": 1500,
    "Signal Jumping": 500
}


# --- Dummy Data for 50 People and their Vehicles ---
DUMMY_PEOPLE_VEHICLES = [
    {"name": "Aarav Sharma", "phone": "9876543210", "vehicle_type": "Motorcycle", "rc_number": "GJ06AB1234"},
    {"name": "Aditi Patel", "phone": "9988776655", "vehicle_type": "Car", "rc_number": "GJ06CD5678"},
    {"name": "Vivaan Singh", "phone": "9123456789", "vehicle_type": "Motorcycle", "rc_number": "GJ06EF9012"},
    {"name": "Diya Gupta", "phone": "9345678901", "vehicle_type": "Car", "rc_number": "GJ06GH3456"},
    {"name": "Reyansh Kumar", "phone": "9567890123", "vehicle_type": "Scooter", "rc_number": "GJ06IJ7890"},
    {"name": "Ananya Devi", "phone": "9789012345", "vehicle_type": "Car", "rc_number": "GJ06KL1234"},
    {"name": "Kian Verma", "phone": "9012345678", "vehicle_type": "Motorcycle", "rc_number": "GJ06MN5678"},
    {"name": "Ishita Rao", "phone": "9234567890", "vehicle_type": "Car", "rc_number": "GJ06OP9012"},
    {"name": "Arjun Reddy", "phone": "9456789012", "vehicle_type": "Scooter", "rc_number": "GJ06QR3456"},
    {"name": "Saanvi Nair", "phone": "9678901234", "vehicle_type": "Car", "rc_number": "GJ06ST7890"},
    {"name": "Dhruv Shah", "phone": "9890123456", "vehicle_type": "Motorcycle", "rc_number": "GJ06UV1234"},
    {"name": "Mira Joshi", "phone": "9001122334", "vehicle_type": "Car", "rc_number": "GJ06WX5678"},
    {"name": "Rohan Das", "phone": "9112233445", "vehicle_type": "Scooter", "rc_number": "GJ06YZ9012"},
    {"name": "Priya Singh", "phone": "9223344556", "vehicle_type": "Car", "rc_number": "GJ06AA2345"},
    {"name": "Kabir Mehta", "phone": "9334455667", "vehicle_type": "Motorcycle", "rc_number": "GJ06BB6789"},
    {"name": "Zara Khan", "phone": "9445566778", "vehicle_type": "Car", "rc_number": "GJ06CC0123"},
    {"name": "Aryan Sharma", "phone": "9556677889", "vehicle_type": "Scooter", "rc_number": "GJ06DD4567"},
    {"name": "Siya Patel", "phone": "9667788990", "vehicle_type": "Car", "rc_number": "GJ06EE8901"},
    {"name": "Viraj Kumar", "phone": "9778899001", "vehicle_type": "Motorcycle", "rc_number": "GJ06FF2345"},
    {"name": "Myra Devi", "phone": "9889900112", "vehicle_type": "Car", "rc_number": "GJ06GG6789"},
    {"name": "Neil Verma", "phone": "9000111223", "vehicle_type": "Scooter", "rc_number": "GJ06HH0123"},
    {"name": "Kiara Rao", "phone": "9111222334", "vehicle_type": "Car", "rc_number": "GJ06II4567"},
    {"name": "Samar Reddy", "phone": "9222333445", "vehicle_type": "Motorcycle", "rc_number": "GJ06JJ8901"},
    {"name": "Nisha Nair", "phone": "9333444556", "vehicle_type": "Car", "rc_number": "GJ06KK2345"},
    {"name": "Vivaan Shah", "phone": "9444555667", "vehicle_type": "Scooter", "rc_number": "GJ06LL6789"},
    {"name": "Anvi Joshi", "phone": "9555666778", "vehicle_type": "Car", "rc_number": "GJ06MM0123"},
    {"name": "Rishi Das", "phone": "9666777889", "vehicle_type": "Motorcycle", "rc_number": "GJ06NN4567"},
    {"name": "Tara Singh", "phone": "9777888990", "vehicle_type": "Car", "rc_number": "GJ06OO8901"},
    {"name": "Dev Mehta", "phone": "9888999001", "vehicle_type": "Scooter", "rc_number": "GJ06PP2345"},
    {"name": "Alia Khan", "phone": "9000011122", "vehicle_type": "Car", "rc_number": "GJ06QQ6789"},
    {"name": "Shlok Sharma", "phone": "9111122233", "vehicle_type": "Motorcycle", "rc_number": "GJ06RR0123"},
    {"name": "Ritika Patel", "phone": "9222233344", "vehicle_type": "Car", "rc_number": "GJ06SS4567"},
    {"name": "Arnav Kumar", "phone": "9333344455", "vehicle_type": "Scooter", "rc_number": "GJ06TT8901"},
    {"name": "Jhanvi Devi", "phone": "9444455566", "vehicle_type": "Car", "rc_number": "GJ06UU2345"},
    {"name": "Parth Verma", "phone": "9555566677", "vehicle_type": "Motorcycle", "rc_number": "GJ06VV6789"},
    {"name": "Sneha Rao", "phone": "9666677788", "vehicle_type": "Car", "rc_number": "GJ06WW0123"},
    {"name": "Kabir Reddy", "phone": "9777788899", "vehicle_type": "Scooter", "rc_number": "GJ06XX4567"},
    {"name": "Aisha Nair", "phone": "9888899900", "vehicle_type": "Car", "rc_number": "GJ06YY8901"},
    {"name": "Krish Shah", "phone": "9000001112", "vehicle_type": "Motorcycle", "rc_number": "GJ06ZZ2345"},
    {"name": "Meera Joshi", "phone": "9111112223", "vehicle_type": "Car", "rc_number": "GJ06A1B234"},
    {"name": "Aditya Das", "phone": "9222223334", "vehicle_type": "Scooter", "rc_number": "GJ06C3D456"},
    {"name": "Divya Singh", "phone": "9333334445", "vehicle_type": "Car", "rc_number": "GJ06E5F678"},
    {"name": "Rahul Mehta", "phone": "9444445556", "vehicle_type": "Motorcycle", "rc_number": "GJ06G7H890"},
    {"name": "Pooja Khan", "phone": "9555556667", "vehicle_type": "Car", "rc_number": "GJ06I9J012"},
    {"name": "Siddharth Sharma", "phone": "9666667778", "vehicle_type": "Scooter", "rc_number": "GJ06K1L234"},
    {"name": "Anushka Patel", "phone": "9777778889", "vehicle_type": "Car", "rc_number": "GJ06M3N456"},
    {"name": "Gaurav Kumar", "phone": "9888889990", "vehicle_type": "Motorcycle", "rc_number": "GJ06O5P678"},
    {"name": "Shruti Devi", "phone": "9000000111", "vehicle_type": "Car", "rc_number": "GJ06Q7R890"},
    {"name": "Harsh Verma", "phone": "9111111222", "vehicle_type": "Scooter", "rc_number": "GJ06S9T012"},
    {"name": "Nandini Rao", "phone": "9222222333", "vehicle_type": "Car", "rc_number": "GJ06U1V234"}
]

# Keep track of which dummy people have been used for challans in the current session
# This ensures a bit more variety, though it resets on app restart
_used_dummy_people_indices = set()

def generate_random_vehicle_number():
    """Generates a random Indian-style vehicle number (e.g., GJ06AB1234)."""
    state_code = "GJ" # Gujarat
    district_code = str(random.randint(1, 99)).zfill(2) # 01 to 99
    series = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
    number = str(random.randint(1000, 9999))
    return f"{state_code}{district_code}{series}{number}"

def generate_challan_number():
    """Generates a dummy challan number (e.g., CHLN-2024-000123)."""
    return f"CHLN-{datetime.now().year}-{random.randint(1, 999999):06d}"

def generate_transaction_id():
    """Generates a dummy transaction ID (e.g., TXN-ABC123XYZ789)."""
    return f"TXN-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))}"

def get_state_from_rc(rc_number):
    """Extracts the state code from an RC number (e.g., 'GJ' from 'GJ06AB1234')."""
    if rc_number and len(rc_number) >= 2:
        return rc_number[:2].upper()
    return "N/A"

def simulate_traffic_data(area_name):
    """
    Simulates real-time vehicle counts (2-wheelers & 4-wheelers)
    and emergency/VIP vehicle presence for lanes within a specific area.
    Also simulates a random traffic violation, using dummy data if available.
    """
    if area_name not in AREAS:
        return None, None # Area not found, return None for both

    lanes_data = {}
    lanes_in_area = AREAS[area_name]

    # Initialize violation status for this simulation cycle
    violation_details = None

    for lane_id in lanes_in_area:
        # Simulate traffic fluctuations
        two_wheelers = random.randint(10, 80)
        four_wheelers = random.randint(5, 60)

        # Simulate emergency vehicle presence with a low probability
        is_emergency = random.choices([True, False], weights=[0.05, 0.95], k=1)[0]
        # Even lower probability for VIP
        is_vip = random.choices([True, False], weights=[0.02, 0.98], k=1)[0]

        density = calculate_lane_density(two_wheelers, four_wheelers)

        lanes_data[lane_id] = {
            'two_wheelers': two_wheelers,
            'four_wheelers': four_wheelers,
            'density': density,
            'is_emergency': is_emergency,
            'is_vip': is_vip,
            'signal_status': 'RED' # Default, will be updated by logic
        }

    # Simulate a traffic violation with a very low probability for the entire area per cycle
    if random.random() < 0.05: # 5% chance per simulation cycle for a violation
        # Try to pick an unused dummy person
        available_indices = list(set(range(len(DUMMY_PEOPLE_VEHICLES))) - _used_dummy_people_indices)
        
        chosen_person = None
        if available_indices:
            chosen_index = random.choice(available_indices)
            chosen_person = DUMMY_PEOPLE_VEHICLES[chosen_index]
            _used_dummy_people_indices.add(chosen_index) # Mark as used
        elif DUMMY_PEOPLE_VEHICLES:
            # If all are used, reset the used set (or pick a random one if we don't want to reset)
            _used_dummy_people_indices.clear()
            chosen_person = random.choice(DUMMY_PEOPLE_VEHICLES)
            _used_dummy_people_indices.add(DUMMY_PEOPLE_VEHICLES.index(chosen_person))
        
        if chosen_person:
            violation_type = random.choice(VIOLATION_TYPES)
            violation_details = {
                'lane_id': random.choice(lanes_in_area), # Assign to a random lane in the area
                'violation_type': violation_type,
                'vehicle_number': chosen_person['rc_number'],
                'owner_name': chosen_person['name'], # This will be "Violator Name" in display
                'owner_phone': chosen_person['phone'],
                'vehicle_type': chosen_person['vehicle_type'],
                'challan_number': generate_challan_number(),
                'transaction_id': generate_transaction_id(),
                'state': get_state_from_rc(chosen_person['rc_number']),
                'fine_amount': FINE_AMOUNTS.get(violation_type, 200) # Get fine amount, default to 200
            }
        else:
            # Fallback to completely random if no dummy people data is available
            random_rc = generate_random_vehicle_number()
            violation_type = random.choice(VIOLATION_TYPES)
            violation_details = {
                'lane_id': random.choice(lanes_in_area),
                'violation_type': violation_type,
                'vehicle_number': random_rc,
                'owner_name': "Random Citizen",
                'owner_phone': "N/A",
                'vehicle_type': random.choice(["Car", "Motorcycle", "Scooter", "Truck"]),
                'challan_number': generate_challan_number(),
                'transaction_id': generate_transaction_id(),
                'state': get_state_from_rc(random_rc),
                'fine_amount': FINE_AMOUNTS.get(violation_type, 200)
            }

    return lanes_data, violation_details # Return violation details along with lane data

def calculate_lane_density(two_wheelers, four_wheelers):
    """
    Calculates a weighted lane density.
    4-wheelers are weighted higher due to larger road footprint.
    """
    return (two_wheelers * 1) + (four_wheelers * 2)

def determine_green_lane(lanes_data):
    """
    Determines which lane should receive the green signal based on priority:
    1. Emergency Vehicles (highest priority)
    2. VIP Movements (high priority)
    3. Lane with the highest traffic density
    """
    green_lane_id = None
    highest_density = -1

    # First, check for emergency vehicles
    for lane_id, data in lanes_data.items():
        if data['is_emergency']:
            print(f"Emergency vehicle detected in {lane_id}. Prioritizing.")
            return lane_id

    # Second, check for VIP movements (if no emergency)
    for lane_id, data in lanes_data.items():
        if data['is_vip']:
            print(f"VIP movement detected in {lane_id}. Prioritizing.")
            return lane_id

    # If no emergency or VIP, find the lane with the highest density
    for lane_id, data in lanes_data.items():
        if data['density'] > highest_density:
            highest_density = data['density']
            green_lane_id = lane_id

    return green_lane_id

def get_available_areas():
    """Returns a list of all predefined area names."""
    return list(AREAS.keys())

if __name__ == '__main__':
    # Example usage for testing the logic
    print("--- Simulating Traffic Data & Logic for Multiple Areas ---")
    for area in get_available_areas():
        print(f"\n--- Area: {area} ---")
        mock_data, violation = simulate_traffic_data(area)
        if mock_data:
            print("Simulated Data:")
            for lane, data in mock_data.items():
                print(f"  {lane}: 2W={data['two_wheelers']}, 4W={data['four_wheelers']}, Density={data['density']}, Emergency={data['is_emergency']}, VIP={data['is_vip']}")
            green = determine_green_lane(mock_data)
            print(f"Determined Green Lane: {green}")
            if violation:
                print(f"  *** VIOLATION DETECTED: {violation['violation_type']} by {violation['vehicle_number']} (Violator: {violation.get('owner_name', 'N/A')}, Phone: {violation.get('owner_phone', 'N/A')}, Challan No: {violation.get('challan_number', 'N/A')}, Txn ID: {violation.get('transaction_id', 'N/A')}, State: {violation.get('state', 'N/A')}, Fine: Rs. {violation.get('fine_amount', 'N/A')}) in {violation['lane_id']} ***")
        time.sleep(1) # Pause for readability
