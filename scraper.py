try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Web scraping dependencies not found. Please install with: pip install selenium webdriver-manager")

import json
from datetime import datetime
import os

class StudySpaceScraper:
    def __init__(self):
        if not SCRAPING_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        self.library_seats_url = "https://seats.library.columbia.edu/allspaces"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        
    def get_library_hours(self, library_name):
        """Get opening hours based on library name"""
        if "Butler" in library_name:
            return "Open 24/7"
        elif "Social Work" in library_name:
            return "Open 10 AM - 9 PM"
        elif "Science" in library_name or "Engineering" in library_name:
            return "Open 9 AM - 3 AM"
        elif "Lehman" in library_name:
            return "Open 9 AM - 11 PM"
        elif "Business" in library_name or "Economics" in library_name or "Uris" in library_name or "Uris" in library_name:
            return "Open 9 AM - 11 PM"
        else:
            return "Open 9 AM - 11 PM"  # Default hours

    def get_library_location(self, library_name):
        """Get location coordinates based on library name"""
        if "Butler" in library_name:
            return {"lat": 40.8064, "lng": -73.9632}
        elif "Social Work" in library_name:
            return {"lat": 40.8103, "lng": -73.9582}
        elif "Science" in library_name or "Engineering" in library_name:
            return {"lat": 40.8103, "lng": -73.9619}
        elif "Lehman" in library_name:
            return {"lat": 40.8078, "lng": -73.9597}
        elif "Business" in library_name or "Economics" in library_name or "Uris" in library_name or "Mezzanine" in library_name:
            return {"lat": 40.8089, "lng": -73.9614}
        else:
            return {"lat": 40.8064, "lng": -73.9632}  # Default to Butler

    def get_library_photo(self, library_name):
        """Get default photo based on library name"""
        if "Butler" in library_name:
            return "butler_room.jpg"
        elif "Social Work" in library_name:
            return "social_work_room.jpg"
        elif "Science" in library_name or "Engineering" in library_name:
            return "science_eng_room.jpg"
        elif "Lehman" in library_name:
            return "lehman_room.jpg"
        elif "Business" in library_name or "Economics" in library_name or "Uris" in library_name:
            return "uris_room.jpg"
        else:
            return "default_room.jpg"

    def update_study_rooms(self):
        """Scrape and update study room data using Selenium"""
        try:
            print("\n=== Starting Scraping Process ===")
            driver = webdriver.Chrome(options=self.options)
            driver.get(self.library_seats_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fc-datagrid-cell-main")))
            
            study_rooms_data = []
            next_id = self.get_next_id()
            
            # Find all room cells
            room_cells = driver.find_elements(By.CLASS_NAME, "fc-datagrid-cell-main")
            print(f"\nFound {len(room_cells)} room cells")
            
            for cell in room_cells:
                try:
                    cell_text = cell.text.strip()
                    if "Capacity" in cell_text:
                        name_part = cell_text.split("(Capacity")[0].strip()
                        capacity = int(cell_text.split("Capacity")[1].replace(")", "").strip())
                        
                        room_parts = name_part.split()
                        room_number = room_parts[0]
                        library_name = " ".join(room_parts[1:])
                        
                        # Get library-specific hours
                        hours = self.get_library_hours(library_name)
                        
                        # Create timeline based on library hours
                        timeline = []
                        if hours == "Open 24/7":
                            # Split 24 hours into segments
                            timeline = [
                                {
                                    "time": "12 AM - 8 AM",
                                    "status": "Available"
                                },
                                {
                                    "time": "8 AM - 4 PM",
                                    "status": "Available"
                                },
                                {
                                    "time": "4 PM - 11:59 PM",
                                    "status": "Available"
                                }
                            ]
                        else:
                            # Get library opening hours
                            hours_parts = hours.split(" ")
                            open_time = f"{hours_parts[1]} {hours_parts[2]}"
                            close_time = f"{hours_parts[4]} {hours_parts[5]}"
                            
                            # Create standard time blocks
                            time_blocks = [
                                (open_time, "1 PM"),
                                ("1 PM", "3 PM"),
                                ("3 PM", close_time)
                            ]
                            
                            # Create timeline entries with proper ranges
                            timeline = [
                                {
                                    "time": f"{start} - {end}",
                                    "status": "Available"
                                }
                                for start, end in time_blocks
                            ]
                        
                        location = self.get_library_location(library_name)
                        photo = self.get_library_photo(library_name)
                        
                        room_data = {
                            "id": next_id,
                            "name": f"{room_number} {library_name}",
                            "hours": hours,
                            "timeline": timeline,
                            "booking_status": "Reservable",
                            "capacity": capacity,
                            "type": "Study Room",
                            "photo": photo,
                            "description": f"Study room {room_number} in {library_name}",
                            "usage_restrictions": "Quiet study only",
                            "location": location,
                            "access_permissions": "All Columbia students",
                            "claimed": False
                        }
                        
                        study_rooms_data.append(room_data)
                        next_id += 1
                
                except Exception as e:
                    print(f"Error processing room cell: {e}")
                    continue
            
            driver.quit()
            return study_rooms_data
            
        except Exception as e:
            print(f"\nERROR in update_study_rooms: {e}")
            if 'driver' in locals():
                driver.quit()
            return []

    def get_next_id(self):
        """Get the next available ID from existing spaces"""
        try:
            with open('data/spaces.json', 'r') as f:
                spaces = json.load(f)
            return max(space["id"] for space in spaces) + 1
        except:
            return 1

    def update_json(self):
        """Update the spaces.json file with new data"""
        try:
            print("\n=== Starting JSON Update ===")
            
            # Load existing data
            print("Loading existing spaces.json")
            with open('data/spaces.json', 'r') as f:
                spaces = json.load(f)
            print(f"Loaded {len(spaces)} existing spaces")
            
            # Get new study room data
            new_rooms = self.update_study_rooms()
            print(f"\nRetrieved {len(new_rooms)} rooms from scraper")
            
            if new_rooms:
                # Create backup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f'data/backup_{timestamp}.json'
                with open(backup_path, 'w') as f:
                    json.dump(spaces, f, indent=4)
                print(f"Backup created at {backup_path}")
                
                # Add or update rooms
                for new_room in new_rooms:
                    # Check if room already exists
                    exists = False
                    for space in spaces:
                        if space["name"] == new_room["name"]:
                            exists = True
                            print(f"Updating existing room: {space['name']}")
                            # Update all fields except id
                            space_id = space["id"]
                            space.update(new_room)
                            space["id"] = space_id  # Preserve original ID
                            break
                    
                    if not exists:
                        print(f"Adding new room: {new_room['name']}")
                        spaces.append(new_room)
                
                # Save updated data
                with open('data/spaces.json', 'w') as f:
                    json.dump(spaces, f, indent=4)
                print(f"\nSaved {len(spaces)} total spaces to spaces.json")
                return True
            
            print("No new data to update")
            return False
            
        except Exception as e:
            print(f"\nERROR in update_json: {e}")
            return False

def main():
    if not SCRAPING_AVAILABLE:
        print("Cannot run scraper: Required dependencies not installed")
        return False
        
    try:
        scraper = StudySpaceScraper()
        print("Starting data update...")
        success = scraper.update_json()
        if success:
            print("Update complete!")
        else:
            print("Update failed - no new data retrieved")
        return success
    except Exception as e:
        print(f"Error during scraping: {e}")
        return False

if __name__ == "__main__":
    main() 