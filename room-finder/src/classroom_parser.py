import csv
import json

def parse_classroom_info():
    classroom_data = {}
    
    with open('src/lib/data/classroom_info.csv', 'r') as file:
        # Skip header row
        reader = csv.DictReader(file)
        
        for row in reader:
            # Clean up the building and room number (remove any whitespace)
            building = row['Building'].strip()
            room_number = row['Room Number'].strip()
            
            # Create the key in the format "Building RoomNumber"
            room_key = f"{building} {room_number}"
            
            # Create the value dictionary with all other information
            room_info = {
                'capacity': int(row['Capacity']) if row['Capacity'].isdigit() else None,
                'room_type': row['Room Type'].strip().lower() if row['Room Type'] else None,
                'seating_style': row['Seating Style'].strip().lower() if row['Seating Style'] else None,
                'table_style': row['Table Style'].strip().lower() if row['Table Style'] else None,
                'shared_tables': int(row['shared tables']) if row['shared tables'].isdigit() else None,
                'board_type': row['Board Type'].strip().lower() if row['Board Type'] else None,
                'has_projector': row['Projector?'].strip().lower() == 'yes' if row['Projector?'] else None
            }
            
            classroom_data[room_key] = room_info
    
    # Write to JSON file
    with open('src/lib/data/classroom_info.json', 'w') as outfile:
        json.dump(classroom_data, outfile, indent=4)

if __name__ == "__main__":
    parse_classroom_info()
