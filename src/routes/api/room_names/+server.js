import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

export async function GET() {
    try {
        const dataPath = path.join(process.cwd(), 'public', 'data', 'room_names.json');
        const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
        return json(data);
    } catch (error) {
        console.error('Error reading room names:', error);
        return json({ error: 'Failed to load room names data' }, { status: 500 });
    }
}