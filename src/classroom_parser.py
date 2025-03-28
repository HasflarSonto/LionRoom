import csv
import json
import os
from pathlib import Path

def get_building_coordinates():
    """
    Returns a dictionary of Columbia University building coordinates
    """
    return {
        "Broadway": {"lat": 40.8090, "lng": -73.9649},
        "Carman": {"lat": 40.8075, "lng": -73.9641},
        "chandler": {"lat": 40.8096, "lng": -73.9616},
        "claremont": {"lat": 40.8111, "lng": -73.9625},
        "engineering_terrace": {"lat": 40.8095, "lng": -73.9600},
        "fayerweather": {"lat": 40.8078, "lng": -73.9604},
        "hamilton": {"lat": 40.8064, "lng": -73.9617},
        "hartley": {"lat": 40.8067, "lng": -73.9641},
        "havemeyer": {"lat": 40.8090, "lng": -73.9622},
        "iab": {"lat": 40.8087, "lng": -73.9596},
        "kent": {"lat": 40.8069, "lng": -73.9622},
        "knox": {"lat": 40.8116, "lng": -73.9625},
        "lewisohn": {"lat": 40.8089, "lng": -73.9628},
        "mathematics": {"lat": 40.8089, "lng": -73.9622},
        "MLK": {"lat": 40.8107, "lng": -73.9604},
        "mudd": {"lat": 40.8095, "lng": -73.9597},
        "northwest corner": {"lat": 40.8097, "lng": -73.9617},
        "philosophy": {"lat": 40.8071, "lng": -73.9609},
        "pupin": {"lat": 40.8101, "lng": -73.9614},
        "schermerhorn": {"lat": 40.8085, "lng": -73.9597},
        "school_of_social_work": {"lat": 40.8068, "lng": -73.9592},
        "shapiro": {"lat": 40.8090, "lng": -73.9595},
        "uris": {"lat": 40.8089, "lng": -73.9613}
    }

def parse_classroom_info():
    classroom_data = {}
    building_coordinates = get_building_coordinates()
    
    with open('public/data/classroom_info.csv', 'r') as file:
        # Skip header row
        reader = csv.DictReader(file)
        
        for row in reader:
            # Clean up the building and room number (remove any whitespace)
            building = row['Building'].strip()
            room_number = row['Room Number'].strip()
            
            # Create the key in the format "Building RoomNumber"
            room_key = f"{building} {room_number}"
            
            # Get building coordinates
            coordinates = building_coordinates.get(building, {"lat": None, "lng": None})
            
            # Create the value dictionary with all other information
            room_info = {
                'capacity': int(row['Capacity']) if row['Capacity'].isdigit() else None,
                'room_type': row['Room Type'].strip().lower() if row['Room Type'] else None,
                'seating_style': row['Seating Style'].strip().lower() if row['Seating Style'] else None,
                'table_style': row['Table Style'].strip().lower() if row['Table Style'] else None,
                'shared_tables': int(row['shared tables']) if row['shared tables'].isdigit() else None,
                'board_type': row['Board Type'].strip().lower() if row['Board Type'] else None,
                'has_projector': row['Projector?'].strip().lower() == 'yes' if row['Projector?'] else None,
                'photos': [],  # Initialize empty photos array
                'location': {
                    'lat': coordinates['lat'],
                    'lng': coordinates['lng'],
                    'building': building
                }
            }
            
            classroom_data[room_key] = room_info

    # Add photos information
    photos_dir = Path('public/data/photos')
    
    # Create a mapping of normalized building names to original building names
    building_map = {
        'uris': 'uris',
        'hamilton': 'hamilton',
        'iab': 'iab',
        'kent': 'kent',
        'lewisohn': 'lewisohn',
        'mudd': 'mudd',
        'pupin': 'pupin',
        'schermerhorn': 'schermerhorn',
        'school_of_social_work': 'school_of_social_work',
        'shapiro': 'shapiro',
        'mlk': 'MLK',
        'mathematics': 'Mathematics'
    }

    # Iterate through all photos in the directory
    for photo_file in photos_dir.glob('*.jpg'):
        file_name = photo_file.stem  # Get filename without extension
        parts = file_name.split('_')
        
        if len(parts) >= 2:
            building = parts[0]
            room_number = parts[1]
            
            # Convert normalized building name to original format
            if building in building_map:
                building = building_map[building]
            
            room_key = f"{building} {room_number}"
            
            # If room exists in classroom_data, add the photo
            if room_key in classroom_data:
                photo_path = f"photos/{photo_file.name}"
                classroom_data[room_key]['photos'].append(photo_path)
                print(f"Added photo {photo_path} to {room_key}")
    
    # Sort photos arrays for each room
    for room_data in classroom_data.values():
        room_data['photos'].sort()
    
    # Write to JSON file
    with open('public/data/classroom_info.json', 'w') as outfile:
        json.dump(classroom_data, outfile, indent=4)
        print("\nSuccessfully updated classroom_info.json with photos and coordinates")

if __name__ == "__main__":
    parse_classroom_info()
