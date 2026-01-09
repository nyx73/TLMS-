from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import traffic_data # Import your traffic logic module
import database # Import your new database module
import os
from datetime import datetime
from fpdf import FPDF # Import FPDF for PDF generation

app = Flask(__name__)
# Generate a strong secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key_here_for_dev_only') # IMPORTANT: Use a strong, random key in production!

# --- Admin Credentials (for demonstration) ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123' # IMPORTANT: In a real app, hash and and store passwords securely!

# Initialize the database on app startup
@app.before_request
def setup_database():
    if not hasattr(app, 'database_initialized'):
        database.init_db()
        app.database_initialized = True

# --- Routes ---

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('select_area')) # Redirect to area selection after login
        else:
            return render_template('login.html', error='Invalid Username or Password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out the user by clearing the session."""
    session.pop('logged_in', None)
    session.pop('selected_area', None) # Clear selected area on logout
    return redirect(url_for('login'))

@app.route('/select_area')
def select_area():
    """
    Displays a page for the admin to select a traffic area.
    Requires user to be logged in.
    """
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    areas = traffic_data.get_available_areas()
    return render_template('select_area.html', areas=areas)


@app.route('/dashboard')
def dashboard():
    """
    Displays the main traffic management dashboard for a specific area.
    Requires user to be logged in and an area to be selected.
    """
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get area name from query parameter or session
    area_name = request.args.get('area')
    if not area_name:
        area_name = session.get('selected_area')

    if not area_name:
        # If no area is specified, redirect to area selection
        return render_template('error.html', message="No area selected."), 400

    # Store selected area in session for persistence
    session['selected_area'] = area_name

    lanes_info, violation_details = traffic_data.simulate_traffic_data(area_name)

    if not lanes_info:
        # Handle case where area name is invalid
        return render_template('error.html', message=f"Area '{area_name}' not found."), 404

    current_green_lane = traffic_data.determine_green_lane(lanes_info)

    # Update the signal status in lanes_info for display
    for lane_id in lanes_info:
        if lane_id == current_green_lane:
            lanes_info[lane_id]['signal_status'] = 'GREEN'
        else:
            lanes_info[lane_id]['signal_status'] = 'RED'

    # Log current traffic data to the database
    database.log_traffic_data(area_name, lanes_info)

    # Add challan if a violation occurred in this simulation cycle
    if violation_details:
        database.add_challan(
            area_name,
            violation_details['lane_id'],
            violation_details['violation_type'],
            violation_details['vehicle_number'],
            violation_details.get('owner_name', 'N/A'),
            violation_details.get('owner_phone', 'N/A'),
            violation_details.get('vehicle_type', 'N/A'),
            violation_details.get('challan_number', 'N/A'),
            violation_details.get('transaction_id', 'N/A'),
            violation_details.get('state', 'N/A'),
            violation_details.get('fine_amount', 0) # Pass fine_amount
        )

    # Get alert threshold for the current area
    alert_threshold = database.get_alert_threshold(area_name)

    # Prepare data for Chart.js
    lane_labels = list(lanes_info.keys())
    lane_densities = [data['density'] for data in lanes_info.values()]

    return render_template('dashboard.html',
                           area_name=area_name,
                           lanes_info=lanes_info,
                           current_green_lane=current_green_lane,
                           lane_labels=lane_labels,
                           lane_densities=lane_densities,
                           alert_threshold=alert_threshold)

@app.route('/api/traffic_data/<area_name>')
def api_traffic_data(area_name):
    """
    API endpoint to provide real-time traffic data for AJAX requests for a specific area.
    This allows the dashboard to update without a full page refresh.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    lanes_info, violation_details = traffic_data.simulate_traffic_data(area_name)

    if not lanes_info:
        return jsonify({"error": f"Area '{area_name}' not found"}), 404

    current_green_lane = traffic_data.determine_green_lane(lanes_info)

    # Update the signal status in lanes_info for display
    for lane_id in lanes_info:
        if lane_id == current_green_lane:
            lanes_info[lane_id]['signal_status'] = 'GREEN'
        else:
            lanes_info[lane_id]['signal_status'] = 'RED'

    # Log current traffic data to the database
    database.log_traffic_data(area_name, lanes_info)

    # Add challan if a violation occurred in this simulation cycle
    if violation_details:
        database.add_challan(
            area_name,
            violation_details['lane_id'],
            violation_details['violation_type'],
            violation_details['vehicle_number'],
            violation_details.get('owner_name', 'N/A'),
            violation_details.get('owner_phone', 'N/A'),
            violation_details.get('vehicle_type', 'N/A'),
            violation_details.get('challan_number', 'N/A'),
            violation_details.get('transaction_id', 'N/A'),
            violation_details.get('state', 'N/A'),
            violation_details.get('fine_amount', 0) # Pass fine_amount
        )

    # Check for alerts
    alert_triggered = False
    alert_message = ""
    alert_threshold = database.get_alert_threshold(area_name)
    congested_lanes = []

    for lane_id, data in lanes_info.items():
        if data['density'] > alert_threshold:
            alert_triggered = True
            congested_lanes.append(f"{lane_id} (Density: {data['density']})")

    if alert_triggered:
        alert_message = f"HIGH CONGESTION ALERT in {area_name}: {', '.join(congested_lanes)}!"

    # Prepare data for Chart.js
    lane_labels = list(lanes_info.keys())
    lane_densities = [data['density'] for data in lanes_info.values()]

    response_data = {
        'lanes_info': lanes_info,
        'current_green_lane': current_green_lane,
        'lane_labels': lane_labels,
        'lane_densities': lane_densities,
        'alert_triggered': alert_triggered,
        'alert_message': alert_message,
        'alert_threshold': alert_threshold
    }
    return jsonify(response_data)

@app.route('/api/historical_traffic_data/<area_name>')
def api_historical_traffic_data(area_name):
    """
    API endpoint to provide historical traffic density data for a specific area.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    # Fetch historical data for all lanes in the area
    historical_data = {}
    lanes_in_area = traffic_data.AREAS.get(area_name, [])
    if not lanes_in_area:
        return jsonify({"error": f"Area '{area_name}' not found or has no defined lanes."}), 404

    for lane_id in lanes_in_area:
        # Fetch data for each lane, limit to a reasonable number for charting
        data = database.get_historical_traffic_data(area_name, lane_id=lane_id, limit=30)
        timestamps = [row[0] for row in data]
        densities = [row[1] for row in data]
        historical_data[lane_id] = {
            'timestamps': timestamps,
            'densities': densities
        }

    return jsonify(historical_data)

@app.route('/api/set_alert_threshold', methods=['POST'])
def api_set_alert_threshold():
    """
    API endpoint to set/update alert thresholds.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    area_name = data.get('area_name')
    max_density = data.get('max_density')

    if not area_name or max_density is None:
        return jsonify({"error": "Missing area_name or max_density"}), 400

    try:
        max_density = int(max_density)
        if max_density < 0:
            raise ValueError("Max density cannot be negative.")
        database.set_alert_threshold(area_name, max_density)
        return jsonify({"success": True, "message": f"Alert threshold for {area_name} set to {max_density}"})
    except ValueError as e:
        return jsonify({"error": f"Invalid max_density value: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/api/challans/<area_name>')
def api_get_challans(area_name):
    """
    API endpoint to get challan data for a specific area.
    Supports optional 'status' filter (e.g., /api/challans/Sayajigunj?status=pending).
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    status_filter = request.args.get('status')
    challans = database.get_challans(area_name, status=status_filter)
    return jsonify(challans)

@app.route('/api/update_challan_status', methods=['POST'])
def api_update_challan_status():
    """
    API endpoint to update a challan's status.
    """
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    challan_id = data.get('challan_id')
    new_status = data.get('new_status')

    if not challan_id or not new_status:
        return jsonify({"error": "Missing challan_id or new_status"}), 400

    try:
        database.update_challan_status(challan_id, new_status)
        return jsonify({"success": True, "message": f"Challan {challan_id} status updated to {new_status}"})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500

@app.route('/generate_pending_challan_pdf/<int:challan_id>')
def generate_pending_challan_pdf(challan_id):
    """
    Generates a PDF for a pending challan (amount to be paid).
    """
    if not session.get('logged_in'):
        return "Unauthorized", 401

    challan = database.get_challan_by_id(challan_id)
    if not challan:
        return "Challan not found.", 404

    if challan['status'] != 'pending':
        return "This is a pending challan print. Please use 'Generate Receipt' for paid challans.", 400

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.set_fill_color(220, 220, 220) # Light grey background
    pdf.cell(0, 10, "Traffic Challan (Amount Due)", 0, 1, 'C', 1)
    pdf.ln(10)

    # Challan Details Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Challan Details:", 0, 1, 'L')
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    # Data for Challan Details table
    challan_data = [
        ("Challan ID:", challan['id']),
        ("Challan Number:", challan.get('challan_number', 'N/A')),
        ("Area:", challan['area_name']),
        ("Lane of Violation:", challan['lane_id']),
        ("Violation Type:", challan['violation_type']),
        ("Violation Timestamp:", datetime.fromisoformat(challan['timestamp']).strftime('%Y-%m-%d %H:%M:%S')),
    ]

    # Draw Challan Details table
    col_width_label = 60 # Width for labels
    col_width_value = 130 # Width for values
    row_height = 7

    for label, value in challan_data:
        pdf.cell(col_width_label, row_height, label, 1, 0, 'L')
        pdf.cell(col_width_value, row_height, str(value), 1, 1, 'L')

    pdf.ln(10)

    # Violator and Vehicle Details Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Violator and Vehicle Details:", 0, 1, 'L')
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    violator_vehicle_data = [
        ("Violator Name:", challan['owner_name']),
        ("Violator Phone:", challan['owner_phone']),
        ("Vehicle Type:", challan['vehicle_type']),
        ("Vehicle Number:", challan['vehicle_number']),
        ("Vehicle State:", challan.get('state', 'N/A')),
    ]

    # Draw Violator and Vehicle Details table
    for label, value in violator_vehicle_data:
        pdf.cell(col_width_label, row_height, label, 1, 0, 'L')
        pdf.cell(col_width_value, row_height, str(value), 1, 1, 'L')

    pdf.ln(10)

    # Amount Due Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Amount Due:", 0, 1, 'L')
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    pdf.cell(col_width_label, row_height, "Fine Amount:", 1, 0, 'L')
    pdf.cell(col_width_value, row_height, f"Rs. {challan.get('fine_amount', 0)}", 1, 1, 'L')
    pdf.cell(col_width_label, row_height, "Status:", 1, 0, 'L')
    pdf.cell(col_width_value, row_height, challan['status'].upper(), 1, 1, 'L')

    pdf.ln(15)

    # Instructions/Disclaimer
    pdf.set_font("Arial", size=9)
    pdf.multi_cell(0, 5, "Please pay this challan amount by visiting the nearest traffic police station or through online payment portals. Failure to pay within the stipulated time may result in additional penalties.")
    pdf.ln(5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 5, "This is an electronically generated challan and does not require a signature.", 0, 1, 'C')

    # Output PDF
    response = Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf')
    response.headers['Content-Disposition'] = f'attachment; filename=challan_print_{challan_id}.pdf'
    return response

@app.route('/generate_paid_challan_pdf/<int:challan_id>')
def generate_paid_challan_pdf(challan_id):
    """
    Generates a PDF receipt for a paid challan in a tabular format.
    """
    if not session.get('logged_in'):
        return "Unauthorized", 401

    challan = database.get_challan_by_id(challan_id)
    if not challan:
        return "Challan not found.", 404

    if challan['status'] != 'paid':
        return "Receipt can only be generated for paid challans. This challan is still pending.", 400

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.set_fill_color(220, 220, 220) # Light grey background
    pdf.cell(0, 10, "Traffic Challan Payment Receipt", 0, 1, 'C', 1)
    pdf.ln(10)

    # Challan Details Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Challan Details:", 0, 1, 'L')
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    # Data for Challan Details table
    challan_data = [
        ("Challan ID:", challan['id']),
        ("Challan Number:", challan.get('challan_number', 'N/A')),
        ("Transaction ID:", challan.get('transaction_id', 'N/A')),
        ("Area:", challan['area_name']),
        ("Lane of Violation:", challan['lane_id']),
        ("Violation Type:", challan['violation_type']),
        ("Violation Timestamp:", datetime.fromisoformat(challan['timestamp']).strftime('%Y-%m-%d %H:%M:%S')),
    ]

    # Draw Challan Details table
    col_width_label = 60 # Width for labels
    col_width_value = 130 # Width for values
    row_height = 7

    for label, value in challan_data:
        pdf.cell(col_width_label, row_height, label, 1, 0, 'L')
        pdf.cell(col_width_value, row_height, str(value), 1, 1, 'L')

    pdf.ln(10)

    # Violator and Vehicle Details Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Violator and Vehicle Details:", 0, 1, 'L')
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    violator_vehicle_data = [
        ("Violator Name:", challan['owner_name']),
        ("Violator Phone:", challan['owner_phone']),
        ("Vehicle Type:", challan['vehicle_type']),
        ("Vehicle Number:", challan['vehicle_number']),
        ("Vehicle State:", challan.get('state', 'N/A')),
    ]

    # Draw Violator and Vehicle Details table
    for label, value in violator_vehicle_data:
        pdf.cell(col_width_label, row_height, label, 1, 0, 'L')
        pdf.cell(col_width_value, row_height, str(value), 1, 1, 'L')

    pdf.ln(10)

    # Payment Summary Section
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Payment Summary:", 0, 1, 'L')
    pdf.set_font("Arial", size=10)
    pdf.ln(2)

    pdf.cell(col_width_label, row_height, "Amount Paid:", 1, 0, 'L')
    pdf.cell(col_width_value, row_height, f"Rs. {challan.get('fine_amount', 0)}", 1, 1, 'L')
    pdf.cell(col_width_label, row_height, "Payment Status:", 1, 0, 'L')
    pdf.cell(col_width_value, row_height, challan['status'].upper(), 1, 1, 'L')
    pdf.cell(col_width_label, row_height, "Payment Date:", 1, 0, 'L')
    pdf.cell(col_width_value, row_height, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1, 1, 'L') # Use current time for payment date

    pdf.ln(15)

    # Footer/Thank you message
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Thank you for your payment.", 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 5, "This is an electronically generated receipt and does not require a signature.", 0, 1, 'C')


    # Output PDF
    response = Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf')
    response.headers['Content-Disposition'] = f'attachment; filename=challan_receipt_{challan_id}.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
