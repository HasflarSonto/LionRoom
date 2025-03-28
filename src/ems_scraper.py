from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import json
import traceback

def extract_pixels(style_string, property_name):
    """
    Extract pixel or percentage value from style string.
    If percentage, converts to pixels based on 1440 total width.
    
    Args:
        style_string: CSS style string
        property_name: Property to extract (e.g., 'width' or 'left')
    
    Returns:
        Integer value in pixels
    """
    # Try to match pixel value first
    px_match = re.search(rf'{property_name}:\s*(\d+)px', style_string)
    if px_match:
        return int(px_match.group(1))
    
    # Try to match percentage value
    pct_match = re.search(rf'{property_name}:\s*(\d+)%', style_string)
    if pct_match:
        percentage = int(pct_match.group(1))
        return int((percentage / 100) * 1440)
    
    return None

def scrape_events():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the webdriver with options
    driver = webdriver.Chrome(options=chrome_options)
    
    # Create a dictionary to store all room data
    room_data_dict = {}

    test = -1

    
    try:
        driver.get("https://ems.cuit.columbia.edu/EmsWebApp/BrowseForSpace.aspx")

        # Scan for all room columns first
        room_columns = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.room-column.column"))
        )
        
        # Initialize dictionary with all room IDs
        for room in room_columns:
            try:
                room_id = room.get_attribute('data-room-id')
                if room_id:
                    room_data_dict[room_id] = {
                        'events': []  # Initialize empty events list for each room
                    }

            except Exception as e:
                print(f"Error processing room column: {str(e)}")
                print(traceback.format_exc())

        #################################################################################################
        # CODE FOR CLOSED HOURS SHOULD BE IMPLEMENTED IN THE FUTURE
        #################################################################################################

        # Add a wait to ensure the page is loaded
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "room-row.grid-row .building-hours"))
        )
        
        # Print page source if needed for debugging
        # print(driver.page_source)
        
        # First, find all room rows with closed elements
        closed_room_rows = driver.find_elements(By.CSS_SELECTOR, ".room-row.grid-row")
      

        print(f"Found {len(closed_room_rows)} closed room rows")  # Debug print

        # Process closed rooms
        for row in closed_room_rows:

            try:

                # Get the room_id from the room row
                room_id = row.get_attribute('data-room-id')
                building_hours = row.find_element(By.CSS_SELECTOR, '.building-hours')
                
                # Initialize room in dictionary if not exists
                if room_id not in room_data_dict:
                    room_data_dict[room_id] = {}
                
                # Add closed room data to the room dictionary
                room_data_dict[room_id]['closed_hours'] = {
                    'width': extract_pixels(building_hours.get_attribute('style'), 'width'),
                    'left_position': extract_pixels(building_hours.get_attribute('style'), 'left'),
                    'is_closed': True
                }
                
                print("\nClosed Room Building Hours:")
                print(f"Room ID: {room_id}")
                print(f"Width: {room_data_dict[room_id]['closed_hours']['width']}px")
                print(f"Left Position: {room_data_dict[room_id]['closed_hours']['left_position']}px")
            except Exception as e:
                # print(f"Error processing closed room: {str(e)}")
                # print(traceback.format_exc())  # Print full traceback
                pass
        



        #################################################################################################
        # EVENT CONTAINER CODE
        #################################################################################################   
        
        # Process event containers
        event_containers = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-container"))
        )
        
        for container in event_containers:
            try:
                room_id = container.get_attribute('data-room-id')
                
                # Initialize room in dictionary if not exists
                if room_id not in room_data_dict:
                    room_data_dict[room_id] = {}
                
                # Create or append event data
                if 'events' not in room_data_dict[room_id]:
                    room_data_dict[room_id]['events'] = []
                
                # Initialize base values from event container
                container_left = extract_pixels(container.get_attribute('style'), 'left')
                
                # Get the main event div
                event_div = container.find_element(By.CLASS_NAME, "event")
                event_width = extract_pixels(event_div.get_attribute('style'), 'width')
                
                # Initialize adjusted positions
                adjusted_left = container_left
                adjusted_width = event_width
                
                # Create event_data dictionary first
                event_data = {
                    'booking_id': container.get_attribute('data-booking-id'),
                    'is_private': container.get_attribute('data-private'),
                    'event_title': container.get_attribute('title'),
                    'original_left': container_left,
                    'original_width': event_width
                }
                

                setup_width = 0
                teardown_width = 0
                # Check for setup div and adjust left position if it exists
                try:
                    setup_div = container.find_element(By.CLASS_NAME, "event-setup")
                    setup_width = extract_pixels(setup_div.get_attribute('style'), 'width')
                    adjusted_left = container_left
                    event_data['setup_width'] = setup_width
                except:
                    event_data['setup_width'] = None
                
                # Check for teardown div and adjust total width if it exists
                try:
                    teardown_div = container.find_element(By.CLASS_NAME, "event-teardown")
                    teardown_width = extract_pixels(teardown_div.get_attribute('style'), 'width')
                    adjusted_width = event_width + teardown_width + setup_width
                    event_data['teardown_width'] = teardown_width
                except:
                    event_data['teardown_width'] = None
                
                # Add adjusted positions to event_data
                event_data['adjusted_left'] = adjusted_left
                event_data['adjusted_width'] = adjusted_width
                
                # Add event to room's events list
                room_data_dict[room_id]['events'].append(event_data)
                
                print(f"\nUpdated Room {room_id} with event:")
                print(f"Event: {event_data}")
                
            except Exception as e:
                print(f"Error processing event container: {e}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        # print("\nPage source:")
        # print(driver.page_source)  # Print page source on error
    finally:
        driver.quit()




    
    # Write the dictionary to a JSON file
    try:
        with open('public/data/room_aval.json', 'w') as f:
            json.dump(room_data_dict, f, indent=4)
        print("\nSuccessfully wrote data to room_aval.json")
        

        


    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        
    return room_data_dict

if __name__ == "__main__":
    room_data = scrape_events()

