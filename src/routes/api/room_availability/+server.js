import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export function GET() {
    try {
        // Update the path to use public/data
        const dataPath = path.resolve('public/data/room_availability.json');
        
        // Check if file exists
        if (!fs.existsSync(dataPath)) {
            return json({ error: 'Room availability data not found' }, { status: 404 });
        }
        
        // Read and parse the JSON file
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        
        // Return the data
        return json(data);
    } catch (error) {
        console.error('Error reading room availability data:', error);
        return json({ error: 'Failed to retrieve room availability data' }, { status: 500 });
    }
}