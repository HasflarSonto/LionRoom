from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re

def extract_pixels(style_string, property_name):
    """Extract pixel value from style string"""
    match = re.search(rf'{property_name}:\s*(\d+)px', style_string)
    return int(match.group(1)) if match else None

def scrape_events():
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # For newer Chrome versions
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the webdriver with options
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to your page
        driver.get("https://ems.cuit.columbia.edu/EmsWebApp/BrowseForSpace.aspx")
        
        # First, find all room rows with closed elements
        closed_room_rows = driver.find_elements(By.CSS_SELECTOR, ".room_row.grid_row:has(.closed-element)")
        
        closed_rooms_data = []
        for row in closed_room_rows:
            try:
                # Get the room_id from the room row
                room_id = row.get_attribute('data-room-id')
                building_hours = row.find_element(By.CLASS_NAME, "building-hours")
                closed_data = {
                    'room_id': room_id,
                    'width': extract_pixels(building_hours.get_attribute('style'), 'width'),
                    'left_position': extract_pixels(building_hours.get_attribute('style'), 'left')
                }
                closed_rooms_data.append(closed_data)
                
                # Print closed room data
                print("\nClosed Room Building Hours:")
                print(f"Room ID: {closed_data['room_id']}")
                print(f"Width: {closed_data['width']}px")
                print(f"Left Position: {closed_data['left_position']}px")
            except Exception as e:
                print(f"Error processing closed room: {e}")
        
        # Wait for event containers to be present
        event_containers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "event-container"))
        )
        
        events_data = []
        
        for container in event_containers:
            event_data = {
                'room_id': container.get_attribute('data-room-id'),
                'booking_id': container.get_attribute('data-booking-id'),
                'is_private': container.get_attribute('data-private'),
                'event_title': container.get_attribute('title'),
                'left_position': extract_pixels(container.get_attribute('style'), 'left')
            }
            
            # Get the main event div
            event_div = container.find_element(By.CLASS_NAME, "event")
            event_data['event_width'] = extract_pixels(event_div.get_attribute('style'), 'width')
            
            # Try to find setup div (if exists)
            try:
                setup_div = container.find_element(By.CLASS_NAME, "event_setup")
                event_data['setup_width'] = extract_pixels(setup_div.get_attribute('style'), 'width')
            except:
                event_data['setup_width'] = None
                
            # Try to find teardown div (if exists)
            try:
                teardown_div = container.find_element(By.CLASS_NAME, "event_teardown")
                event_data['teardown_width'] = extract_pixels(teardown_div.get_attribute('style'), 'width')
            except:
                event_data['teardown_width'] = None
            
            events_data.append(event_data)
            
            # Print the data for each event
            print(f"\nRoom ID: {event_data['room_id']}")
            print(f"Event: {event_data['event_title']}")
            print(f"Position from left: {event_data['left_position']}px")
            print(f"Event width: {event_data['event_width']}px")
            print(f"Setup width: {event_data['setup_width']}px")
            print(f"Teardown width: {event_data['teardown_width']}px")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        
    return {'events': events_data, 'closed_rooms': closed_rooms_data}

if __name__ == "__main__":
    scrape_events()
