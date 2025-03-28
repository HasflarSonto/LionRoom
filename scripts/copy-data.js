import fs from 'fs';
import path from 'path';

const publicDataDir = path.join(process.cwd(), 'public', 'data');

// Ensure the directory exists
fs.mkdirSync(publicDataDir, { recursive: true });

// List of files to copy
const files = [
    'room_availability.json',
    'classroom_info.json',
    'room_id.json',
    'buildings.json'
];

// Copy each file
files.forEach(file => {
    const sourcePath = path.join(process.cwd(), 'src', 'lib', 'data', file);
    const destPath = path.join(publicDataDir, file);
    
    if (fs.existsSync(sourcePath)) {
        fs.copyFileSync(sourcePath, destPath);
        console.log(`Copied ${file} to public/data`);
    } else {
        console.warn(`Warning: ${file} not found in source directory`);
    }
}); 