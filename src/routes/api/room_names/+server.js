import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export function GET() {
    try {
        // Update the path to use public/data
        const dataPath = path.resolve('public/data/room_id.json');
        
        // Check if file exists
        if (!fs.existsSync(dataPath)) {
            return json({ error: 'Room names data not found' }, { status: 404 });
        }
        
        // Read and parse the JSON file
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        
        // Return the data
        return json(data);
    } catch (error) {
        console.error('Error reading room names data:', error);
        return json({ error: 'Failed to retrieve room names data' }, { status: 500 });
    }
}