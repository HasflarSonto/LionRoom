import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function GET({ params }) {
    try {
        const dataPath = path.join(process.cwd(), 'public', 'data', 'room_availability.json');
        
        if (!fs.existsSync(dataPath)) {
            return json({ error: 'Room availability data not found' }, { status: 404 });
        }

        const rawData = fs.readFileSync(dataPath, 'utf8');
        const data = JSON.parse(rawData);
        
        // Get availability for specific room ID
        const roomAvailability = data[params.id] || [];
        
        return json(roomAvailability);
    } catch (error) {
        console.error('Error reading room availability:', error);
        return json({ error: 'Failed to retrieve room availability' }, { status: 500 });
    }
} 