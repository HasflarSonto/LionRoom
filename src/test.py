import json

# Load buildings.json
building_room_ids = set()
with open('src/lib/data/buildings.json', 'r') as f:
    buildings_data = json.load(f)
    for building in buildings_data:
        for room_id in buildings_data[building]:
            building_room_ids.add(room_id)

# Load room_id.json
room_id_keys = set()
with open('src/lib/data/room_id.json', 'r') as f:
    rooms_data = json.load(f)
    for room_id in rooms_data:
        room_id_keys.add(room_id)

# Check for differences
print(f"Total rooms in buildings.json: {len(building_room_ids)}")
print(f"Total rooms in room_id.json: {len(room_id_keys)}")

# Check if room_id.json has rooms not in buildings.json
rooms_missing_from_buildings = room_id_keys - building_room_ids
if rooms_missing_from_buildings:
    print("\nRooms in room_id.json but missing from buildings.json:")
    for room_id in sorted(rooms_missing_from_buildings):
        print(f"ID: {room_id}, Name: {rooms_data[room_id]}")

# Check if buildings.json has rooms not in room_id.json
rooms_missing_from_room_id = building_room_ids - room_id_keys
if rooms_missing_from_room_id:
    print("\nRooms in buildings.json but missing from room_id.json:")
    for room_id in sorted(rooms_missing_from_room_id):
        # Find which building contains this room
        for building in buildings_data:
            if room_id in buildings_data[building]:
                print(f"ID: {room_id}, Name: {buildings_data[building][room_id]}, Building: {building}")
                break

# Check if all rooms match completely
if not rooms_missing_from_buildings and not rooms_missing_from_room_id:
    print("\nPerfect match! All rooms in both files match exactly.")
else:
    print(f"\nMismatch summary: {len(rooms_missing_from_buildings)} rooms missing from buildings.json, {len(rooms_missing_from_room_id)} rooms missing from room_id.json")






