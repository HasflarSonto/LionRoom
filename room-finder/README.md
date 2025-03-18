# Lion Room - Columbia Room Availability Tracker

A web application that displays real-time room availability across Columbia University's campus.

## Features

- Shows 24-hour availability timeline for each room
- Current time marker that automatically scrolls to center
- View rooms by building or see all rooms at once
- Auto-refreshes data every 5 minutes
- Visually represents partial hour availability

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Node.js and npm
- Chrome WebDriver for Selenium

### Dependencies Installation

1. Install Python dependencies:
```bash
python3 -m pip install selenium schedule
```

2. Install the SvelteKit application dependencies:
```bash
npm install
```

### Running the Application

1. Start the automated data scheduler (runs every 5 minutes):
```bash
python3 src/scheduler.py
```

2. In a separate terminal, start the SvelteKit development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173` or the URL displayed in your terminal.

## How It Works

### Data Pipeline

1. **Data Collection**: `ems_scraper.py` uses Selenium to scrape the Columbia EMS reservation system and creates `room_aval.json`.
2. **Data Processing**: `room_hours.py` processes the scraped data to determine room availability and creates `room_availability.json`.
3. **Data Serving**: SvelteKit API endpoints serve this data to the frontend.
4. **Auto-Refresh**: The frontend checks for data updates every minute and refreshes when new data is available.

### Scheduler

The `scheduler.py` script coordinates this pipeline to run every 5 minutes:
- Runs the scraper
- Processes the data
- Creates a timestamp file
- The frontend checks this timestamp to know when to refresh

## Project Structure

- `src/ems_scraper.py` - Web scraper for room data
- `src/room_hours.py` - Processes scraped data into availability time ranges
- `src/scheduler.py` - Coordinates the automatic data pipeline
- `src/lib/data/` - Directory for data files
- `src/lib/components/Room.svelte` - Room component with timeline display
- `src/routes/+page.svelte` - Main application page
- `src/routes/api/` - API endpoints to serve data

## Customization

- Edit the scraper to target different data sources
- Modify the UI colors and styling in the Svelte components
- Adjust the scheduler timing by changing the interval in `scheduler.py`
