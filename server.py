from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import json
import os
from datetime import datetime
import pytz

app = Flask(__name__)

# Load study space data
DATA_FILE = "data/spaces.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def get_nyc_time():
    nyc_tz = pytz.timezone('America/New_York')
    return datetime.now(nyc_tz)

def parse_time(time_str):
    """Convert time string (e.g., '9 AM', '11 PM') to 24-hour format"""
    try:
        if time_str == "Midnight":
            return 0
        if time_str == "24/7":
            return -1  # Special case for 24/7
        
        time_parts = time_str.split(" ")
        hour = int(time_parts[0])
        if time_parts[1] == "PM" and hour != 12:
            hour += 12
        elif time_parts[1] == "AM" and hour == 12:
            hour = 0
        return hour
    except:
        return -1  # Return -1 for any parsing errors or 24/7

def calculate_availability(timeline, hours):
    current_time = get_nyc_time()
    current_hour = current_time.hour
    current_minute = current_time.minute
    
    # First check if the space is open based on hours
    if hours != "Open 24/7":
        try:
            # Parse opening hours
            hours_parts = hours.split(" ")
            if len(hours_parts) >= 4:  # Format: "Open 9 AM - 11 PM"
                opening_time = parse_time(f"{hours_parts[1]} {hours_parts[2]}")
                closing_time = parse_time(f"{hours_parts[4]} {hours_parts[5]}")
                
                # Check if current time is outside opening hours
                if closing_time > opening_time:  # Normal schedule
                    if current_hour < opening_time or current_hour >= closing_time:
                        return {"status": "Closed", "hours": hours}
                else:  # Overnight schedule (e.g., 9 PM - 2 AM)
                    if current_hour < opening_time and current_hour >= closing_time:
                        return {"status": "Closed", "hours": hours}
        except:
            pass  # If there's any error parsing hours, continue to timeline check
    
    # If no timeline or space is 24/7, return open
    if not timeline:
        return {"status": "Open", "hours": hours}
    
    # Check timeline for current status
    for slot in timeline:
        start_time = slot["time"].split(" - ")[0]
        end_time = slot["time"].split(" - ")[1]
        
        start_hour = parse_time(start_time)
        end_hour = parse_time(end_time)
        
        if start_hour <= current_hour < end_hour:
            return {
                "status": slot["status"],
                "hours": hours,
                "current_slot": slot["time"]
            }
    
    # If we're within opening hours but not in any booked slot, space is available
    return {"status": "Available", "hours": hours}

def calculate_availability_at_time(timeline, hours, check_hour, check_minute=0):
    """Calculate availability for a specific time instead of current time"""
    # First check if the space is open based on hours
    if hours != "Open 24/7":
        try:
            hours_parts = hours.split(" ")
            if len(hours_parts) >= 4:
                opening_time = parse_time(f"{hours_parts[1]} {hours_parts[2]}")
                closing_time = parse_time(f"{hours_parts[4]} {hours_parts[5]}")
                
                if closing_time > opening_time:  # Normal schedule
                    if check_hour < opening_time or check_hour >= closing_time:
                        return {"status": "Closed", "hours": hours}
                else:  # Overnight schedule
                    if check_hour < opening_time and check_hour >= closing_time:
                        return {"status": "Closed", "hours": hours}
        except:
            pass

    if not timeline:
        return {"status": "Open", "hours": hours}
    
    # Check timeline for status at specified time
    for slot in timeline:
        start_time = slot["time"].split(" - ")[0]
        end_time = slot["time"].split(" - ")[1]
        
        start_hour = parse_time(start_time)
        end_hour = parse_time(end_time)
        
        if start_hour <= check_hour < end_hour:
            status = "Open" if slot["status"] == "Available" else slot["status"]
            return {
                "status": status,
                "hours": hours,
                "current_slot": slot["time"]
            }
    
    return {"status": "Open", "hours": hours}

@app.route('/')
def home():
    spaces = load_data()
    
    # Calculate current status for each space and convert "Available" to "Open"
    for space in spaces:
        availability_info = calculate_availability(space["timeline"], space["hours"])
        status = availability_info["status"]
        space["current_status"] = "Open" if status == "Available" else status

    # Helper function to get sorted spaces by type with minimum count
    def get_spaces_by_type(space_type, min_count=3):
        typed_spaces = [s for s in spaces if s["type"] == space_type]
        # Sort by status priority: Open first, then Booked, then Closed
        sorted_spaces = sorted(typed_spaces, key=lambda x: (
            2 if x["current_status"] == "Closed" else 
            1 if x["current_status"] == "Booked" else 0
        ))
        # Debug print to check sorting
        print(f"Sorted {space_type}:", [(s["name"], s["current_status"]) for s in sorted_spaces])
        return sorted_spaces[:min_count]
    
    # Get spaces for each type
    classrooms = get_spaces_by_type("Classroom")
    study_rooms = get_spaces_by_type("Study Room")
    reading_rooms = get_spaces_by_type("Reading Room")
    
    # Combine all spaces for the template
    all_spaces = classrooms + study_rooms + reading_rooms
    
    return render_template('index.html', spaces=all_spaces)

@app.route('/search')
def search():
    query = request.args.get('q', '').lower().strip()
    check_time = request.args.get('check_time', '')
    status_filter = request.args.get('status_filter', 'all')
    claim_filter = request.args.get('claim_filter', 'all')
    type_filter = request.args.get('type_filter', 'all')
    min_capacity = request.args.get('min_capacity', '')
    
    spaces = load_data()
    
    # Filter spaces based on search query
    if query:
        filtered_spaces = []
        for space in spaces:
            # Check different types of matches
            name_match = query in space['name'].lower()
            type_match = query in space['type'].lower()
            
            # Check status matches (case-insensitive exact word match)
            current_status = space.get('current_status', '').lower()
            status_match = (query == current_status or 
                          (query == 'open' and current_status == 'available') or
                          (query == 'available' and current_status == 'open'))
            
            # Check claim status matches (case-insensitive exact word match)
            claim_status = 'claimed' if space.get('claimed', False) else 'unclaimed'
            claim_match = query == claim_status.lower()
            
            if any([name_match, type_match, status_match, claim_match]):
                space['match_info'] = {
                    'name_match': query if name_match else None,
                    'type_match': query if type_match else None,
                    'status_match': query if status_match else None,
                    'claim_match': query if claim_match else None
                }
                filtered_spaces.append(space)
        spaces = filtered_spaces

    # Calculate availability for each space before applying filters
    for space in spaces:
        if check_time:
            hour = int(check_time.split(':')[0])
            minute = int(check_time.split(':')[1])
            availability_info = calculate_availability_at_time(space["timeline"], space["hours"], hour, minute)
        else:
            availability_info = calculate_availability(space["timeline"], space["hours"])
        space["current_status"] = "Open" if availability_info["status"] == "Available" else availability_info["status"]
    
    # Apply advanced search filters
    if status_filter != 'all':
        if status_filter == 'available':
            spaces = [s for s in spaces if s['current_status'] == 'Open']
        elif status_filter == 'booked':
            spaces = [s for s in spaces if s['current_status'] == 'Booked']
        elif status_filter == 'closed':
            spaces = [s for s in spaces if s['current_status'] == 'Closed']

    if claim_filter != 'all':
        if claim_filter == 'claimed':
            spaces = [s for s in spaces if s.get('claimed', False)]
        elif claim_filter == 'unclaimed':
            spaces = [s for s in spaces if not s.get('claimed', False)]
    
    # Filter by room type
    if type_filter != 'all':
        spaces = [s for s in spaces if s['type'] == type_filter]
    
    # Filter by minimum capacity
    if min_capacity:
        try:
            min_cap = int(min_capacity)
            spaces = [s for s in spaces if s['capacity'] >= min_cap]
        except ValueError:
            pass
    
    # Sort spaces by status (Open first, then Booked, then Closed)
    def status_sort_key(space):
        if space["current_status"] == "Open":
            return 0
        elif space["current_status"] == "Booked":
            return 1
        else:  # Closed
            return 2
    
    spaces = sorted(spaces, key=status_sort_key)
    
    return render_template('search.html', 
                         spaces=spaces,
                         count=len(spaces),
                         query=query,
                         check_time=check_time,
                         status_filter=status_filter,
                         claim_filter=claim_filter,
                         type_filter=type_filter,
                         min_capacity=min_capacity)

@app.route('/view/<int:space_id>')
def view_space(space_id):
    spaces = load_data()
    space = next((s for s in spaces if s["id"] == space_id), None)
    if space:
        # Calculate real-time availability
        availability_info = calculate_availability(space["timeline"], space["hours"])
        space["current_status"] = availability_info["status"]
        space["hours"] = availability_info["hours"]
    return render_template("view.html", space=space)

def validate_hours_format(hours):
    """Validate the hours format"""
    if hours == "Open 24/7":
        return True
    
    try:
        # Check basic format
        if not hours.startswith("Open "):
            return False
        
        # Split the time range
        time_part = hours[5:]  # Remove "Open " prefix
        start_time, end_time = time_part.split(" - ")
        
        # Validate each time
        valid_times = ["24/7", "Midnight"] + [f"{h} AM" for h in range(1, 13)] + [f"{h} PM" for h in range(1, 13)]
        
        return start_time in valid_times and end_time in valid_times
    except:
        return False

@app.route('/add', methods=['GET', 'POST'])
def add_space():
    if request.method == 'GET':
        return render_template("add.html")
        
    try:
        # Get form data and validate it exists first
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        
        if lat is None or lng is None:
            return jsonify({
                'success': False,
                'error': 'Latitude and longitude are required.'
            })
            
        # Convert to float after validating existence
        lat = float(lat)
        lng = float(lng)
        
        # Rest of the validation and space creation logic
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return jsonify({
                'success': False,
                'error': 'Invalid coordinates. Latitude must be between -90 and 90, and longitude between -180 and 180.'
            })
            
        hours = request.form["hours"]
        if not validate_hours_format(hours):
            return jsonify({
                "success": False,
                "error": "Invalid hours format. Please use the format 'Open [Start Time] - [End Time]' or 'Open 24/7'"
            })
                
        spaces = load_data()
        new_id = max([s["id"] for s in spaces], default=0) + 1
        
        # Create timeline from form data
        timeline = []
        times = request.form.getlist('timeline_time[]')
        statuses = request.form.getlist('timeline_status[]')
        for time, status in zip(times, statuses):
            if time:  # Only add if time is not empty
                timeline.append({"time": time, "status": status})

        new_space = {
            "id": new_id,
            "name": request.form["name"],
            "hours": hours,
            "timeline": timeline,
            "booking_status": request.form["booking_status"],
            "capacity": int(request.form["capacity"]),
            "type": request.form["type"],
            "photo": request.form["photo"],
            "description": request.form["description"],
            "usage_restrictions": request.form["usage_restrictions"],
            "location": {"lat": lat, "lng": lng},
            "access_permissions": request.form["access_permissions"],
            "claimed": False
        }
        spaces.append(new_space)
        save_data(spaces)
        
        return jsonify({
            "success": True,
            "message": "New study space successfully created!",
            "space_id": new_id,
            "view_url": url_for("view_space", space_id=new_id)
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Latitude and longitude must be valid numbers.'
        })
            
    return render_template("add.html")

@app.route('/edit/<int:space_id>', methods=['GET', 'POST'])
def edit_space(space_id):
    spaces = load_data()
    space = next((s for s in spaces if s["id"] == space_id), None)
    if not space:
        return "Space not found", 404

    if request.method == 'POST':
        hours = request.form["hours"]
        if not validate_hours_format(hours):
            flash("Invalid hours format. Please use the format 'Open [Start Time] - [End Time]' or 'Open 24/7'", "error")
            return render_template("edit.html", space=space)
            
        # Create timeline from form data
        timeline = []
        times = request.form.getlist('timeline_time[]')
        statuses = request.form.getlist('timeline_status[]')
        for time, status in zip(times, statuses):
            if time:  # Only add if time is not empty
                timeline.append({"time": time, "status": status})

        space.update({
            "name": request.form["name"],
            "hours": hours,
            "timeline": timeline,
            "booking_status": request.form["booking_status"],
            "capacity": int(request.form["capacity"]),
            "type": request.form["type"],
            "photo": request.form["photo"],
            "description": request.form["description"],
            "usage_restrictions": request.form["usage_restrictions"],
            "location": {"lat": float(request.form["lat"]), "lng": float(request.form["lng"])},
            "access_permissions": request.form["access_permissions"]
        })
        save_data(spaces)
        return redirect(url_for("view_space", space_id=space_id))

    return render_template("edit.html", space=space)

@app.route('/delete/<int:space_id>', methods=['POST'])
def delete_space(space_id):
    spaces = load_data()
    spaces = [s for s in spaces if s["id"] != space_id]
    save_data(spaces)
    return redirect(url_for("home"))

@app.route('/map')
def map():
    return render_template("map.html")


@app.route('/claim/<int:space_id>', methods=['POST'])
def claim_space(space_id):
    try:
        data = request.get_json()
        spaces = load_data()
        
        # Find the space and update its claimed status
        for space in spaces:
            if space['id'] == space_id:
                space['claimed'] = data['claimed']
                save_data(spaces)
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Space not found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/unclaim/<int:space_id>', methods=['POST'])
def unclaim_space(space_id):
    spaces = load_data()
    space = next((s for s in spaces if s["id"] == space_id), None)
    if not space:
        return jsonify({"success": False, "error": "Space not found"}), 404
    space["claimed"] = False
    save_data(spaces)
    return jsonify({"success": True, "claimed": False})


@app.route('/api/spaces')
def api_spaces():
    return jsonify(load_data())

@app.route('/api/space-status/<int:space_id>')
def get_space_status(space_id):
    spaces = load_data()
    space = next((s for s in spaces if s["id"] == space_id), None)
    if space:
        availability_info = calculate_availability(space["timeline"], space["hours"])
        return jsonify({
            "status": availability_info["status"],
            "hours": availability_info["hours"]
        })
    return jsonify({"error": "Space not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)
