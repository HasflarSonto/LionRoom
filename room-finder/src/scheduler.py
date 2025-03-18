import schedule
import time
import subprocess
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('room_scheduler')

def run_data_pipeline():
    """Run the complete data pipeline: scrape data, process hours, and update timestamp"""
    logger.info("Starting data pipeline...")
    
    try:
        # Run the EMS scraper
        logger.info("Running EMS scraper...")
        subprocess.run(["python", "src/ems_scraper.py"], check=True)
        logger.info("EMS scraper completed successfully")
        
        # Run the room hours processor
        logger.info("Processing room hours...")
        subprocess.run(["python", "src/room_hours.py"], check=True)
        logger.info("Room hours processed successfully")
        
        # Create or update a timestamp file for the frontend to check
        timestamp = datetime.now().isoformat()
        with open('src/lib/data/last_update.json', 'w') as f:
            f.write(f'{{"timestamp": "{timestamp}"}}')
        logger.info(f"Data pipeline completed successfully. Timestamp: {timestamp}")
        
    except Exception as e:
        logger.error(f"Error in data pipeline: {str(e)}")

def main():
    logger.info("Starting room availability scheduler")
    
    # Create data directory if it doesn't exist
    os.makedirs('src/lib/data', exist_ok=True)
    
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