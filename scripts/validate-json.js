import fs from 'fs';
import path from 'path';

const filePath = path.join(process.cwd(), 'static', 'data', 'room_availability.json');

try {
    console.log('Checking file:', filePath);
    const rawData = fs.readFileSync(filePath, 'utf-8');
    console.log('Raw data first 100 chars:', rawData.substring(0, 100));
    
    const parsed = JSON.parse(rawData);
    console.log('JSON is valid');
    console.log('Data structure:', typeof parsed);
    console.log('Keys:', Object.keys(parsed));
} catch (error) {
    console.error('Error validating JSON:', error);
} 