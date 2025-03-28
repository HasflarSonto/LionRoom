import subprocess
import os
import sys
from datetime import datetime

# Setup absolute paths based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Go up one level from src/ to the project root
DATA_DIR = os.path.join(BASE_DIR, 'public', 'data')

def ensure_data_directories():
    """Make sure all required data directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Ensured data directory exists at: {DATA_DIR}")

def run_data_pipeline():
    """Run the complete data pipeline: scrape data and process hours"""
    print("Starting data pipeline...")
    ensure_data_directories()
    
    try:
        # Run the EMS scraper
        print("Running EMS scraper...")
        scraper_path = os.path.join(SCRIPT_DIR, "ems_scraper.py")
        result = subprocess.run(
            [sys.executable, scraper_path], 
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        print(f"EMS scraper output: {result.stdout}")
        if result.stderr:
            print(f"EMS scraper warnings/errors: {result.stderr}")
        
        # Run the room hours processor
        print("Processing room hours...")
        hours_path = os.path.join(SCRIPT_DIR, "room_hours.py")
        result = subprocess.run(
            [sys.executable, hours_path], 
            check=True,
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        
        print(f"Room hours processor output: {result.stdout}")
        if result.stderr:
            print(f"Room hours processor warnings/errors: {result.stderr}")
        
        # Update timestamp
        timestamp = datetime.now().isoformat()
        timestamp_path = os.path.join(DATA_DIR, "last_update.json")
        with open(timestamp_path, 'w') as f:
            f.write(f'{{"timestamp": "{timestamp}"}}')
        
        print(f"Data pipeline completed successfully at: {timestamp}")
        
    except subprocess.CalledProcessError as e:
        print(f"Process error in data pipeline: {str(e)}")
        print(f"Process stdout: {e.stdout}")
        print(f"Process stderr: {e.stderr}")
    except Exception as e:
        print(f"Error in data pipeline: {str(e)}")

if __name__ == "__main__":
    run_data_pipeline() 