import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function GET() {
    try {
        const dataPath = path.resolve('public/data/classroom_info.json');
        
        if (!fs.existsSync(dataPath)) {
            return json({ error: 'Classroom info data not found' }, { status: 404 });
        }
        
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        return json(data);
    } catch (error) {
        console.error('Error reading classroom info:', error);
        return json({ error: 'Failed to retrieve classroom info' }, { status: 500 });
    }
}