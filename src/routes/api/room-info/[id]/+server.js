import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function GET({ params }) {
    try {
        const dataPath = path.join(process.cwd(), 'public', 'data', 'classroom_info.json');
        
        if (!fs.existsSync(dataPath)) {
            return json({ error: 'Room info data not found' }, { status: 404 });
        }

        const rawData = fs.readFileSync(dataPath, 'utf8');
        const data = JSON.parse(rawData);
        
        // Get info for specific room ID
        const roomInfo = data[params.id];
        
        if (!roomInfo) {
            return json({ error: 'Room not found' }, { status: 404 });
        }

        return json(roomInfo);
    } catch (error) {
        console.error('Error reading room info:', error);
        return json({ error: 'Failed to retrieve room info' }, { status: 500 });
    }
} 