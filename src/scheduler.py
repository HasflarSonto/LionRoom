import schedule
import time
import subprocess
import os
import logging
import sys
from datetime import datetime

# Setup absolute paths based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Go up one level from src/ to the project root
DATA_DIR = os.path.join(BASE_DIR, 'src', 'lib', 'data')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(SCRIPT_DIR, "scheduler.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('room_scheduler')

def ensure_data_directories():
    """Make sure all required data directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    logger.info(f"Ensured data directory exists at: {DATA_DIR}")

def run_data_pipeline():
    """Run the complete data pipeline: scrape data, process hours, and update timestamp"""
    logger.info("Starting data pipeline...")
    ensure_data_directories()
    
    try:
        # Run the EMS scraper with proper working directory
        logger.info("Running EMS scraper...")
        scraper_path = os.path.join(SCRIPT_DIR, "ems_scraper.py")
        result = subprocess.run(
            [sys.executable, scraper_path], 
            check=True,
            cwd=BASE_DIR,  # Set working directory to project root
            capture_output=True,
            text=True
        )
        
        logger.info(f"EMS scraper output: {result.stdout}")
        if result.stderr:
            logger.warning(f"EMS scraper warnings/errors: {result.stderr}")
        
        # Verify room_aval.json was created
        room_aval_path = os.path.join(DATA_DIR, "room_aval.json")
        if not os.path.exists(room_aval_path):
            logger.error(f"room_aval.json not created at: {room_aval_path}")
            raise FileNotFoundError(f"room_aval.json not found at: {room_aval_path}")
        
        # Run the room hours processor
        logger.info("Processing room hours...")
        hours_path = os.path.join(SCRIPT_DIR, "room_hours.py")
        result = subprocess.run(
            [sys.executable, hours_path], 
            check=True,
            cwd=BASE_DIR,  # Set working directory to project root
            capture_output=True,
            text=True
        )
        
        logger.info(f"Room hours processor output: {result.stdout}")
        if result.stderr:
            logger.warning(f"Room hours processor warnings/errors: {result.stderr}")
        
        # Verify room_availability.json was created
        room_availability_path = os.path.join(DATA_DIR, "room_availability.json")
        if not os.path.exists(room_availability_path):
            logger.error(f"room_availability.json not created at: {room_availability_path}")
            raise FileNotFoundError(f"room_availability.json not found at: {room_availability_path}")
        
        # Create or update a timestamp file for the frontend to check
        timestamp = datetime.now().isoformat()
        timestamp_path = os.path.join(DATA_DIR, "last_update.json")
        with open(timestamp_path, 'w') as f:
            f.write(f'{{"timestamp": "{timestamp}"}}')
        
        logger.info(f"Data pipeline completed successfully. Timestamp: {timestamp}")
        logger.info(f"Files updated at: {DATA_DIR}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Process error in data pipeline: {str(e)}")
        logger.error(f"Process stdout: {e.stdout}")
        logger.error(f"Process stderr: {e.stderr}")
    except Exception as e:
        logger.error(f"Error in data pipeline: {str(e)}")

def main():
    logger.info("Starting room availability scheduler")
    
    # Create data directory if it doesn't exist
    ensure_data_directories()
    
    # Run once at startup
    run_data_pipeline()
    
    # Schedule to run every 5 minutes
    schedule.every(5).minutes.do(run_data_pipeline)
    
    logger.info("Scheduler running, will update every 5 minutes")
    
    # Run the scheduling loop
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 