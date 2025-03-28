import { copyFileSync, mkdirSync } from 'fs';
import { join } from 'path';

// Ensure directories exist
mkdirSync('static/data', { recursive: true });
mkdirSync('static/data/photos', { recursive: true });

// Copy JSON files
const jsonFiles = [
    'buildings.json',
    'room_availability.json',
    'last_update.json',
    // Add other JSON files here
];

jsonFiles.forEach(file => {
    copyFileSync(
        join('src', 'lib', 'data', file),
        join('static', 'data', file)
    );
});

// Copy photos
// Add logic to copy photos if needed 