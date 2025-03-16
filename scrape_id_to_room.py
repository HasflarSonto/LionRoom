from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

def scrape_room_columns():
    # Initialize the webdriver (Chrome in this example)
    driver = webdriver.Chrome()
    
    try:
        # # Navigate to the login page first (you'll need to find the correct login URL)
        # driver.get("https://ems.cuit.columbia.edu/")
        
        # # Add login logic here
        # # driver.find_element(By.ID, "username").send_keys("your_username")
        # # driver.find_element(By.ID, "password").send_keys("your_password")
        # # driver.find_element(By.ID, "login-button").click()
        
        # # Wait for login to complete and then navigate to the target page
        # time.sleep(2)  # Add appropriate wait time
        driver.get("https://ems.cuit.columbia.edu/EmsWebApp/BrowseForSpace.aspx")

        # Wait for the room-column elements to be present
        room_columns = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.room-column.column"))
        )
        
        # Create a dictionary to store the room data
        room_data = {}
        
        # Process each room column
        for column in room_columns:
            title = column.get_attribute('title')
            room_id = column.get_attribute('data-room-id')
            building_id = column.get_attribute('data-building-id')
            
            # Add to dictionary with room_id as key and title as value
            room_data[room_id] = title
            
        # Write to JSON file
        with open('rooms.json', 'w') as f:
            json.dump(room_data, f, indent=4)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_room_columns()
