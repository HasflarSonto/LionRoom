import { json } from '@sveltejs/kit';
import fs from 'fs';
import path from 'path';

// Path to bookings JSON file
const bookingsFilePath = path.resolve('public/data/bookings.json');

// Function to read the current bookings
function readBookings() {
    try {
        // Create file if it doesn't exist
        if (!fs.existsSync(bookingsFilePath)) {
            fs.writeFileSync(bookingsFilePath, '{}', 'utf8');
            return {};
        }
        
        // Read and parse existing bookings
        const data = fs.readFileSync(bookingsFilePath, 'utf8');
        return data ? JSON.parse(data) : {};
    } catch (error) {
        console.error('Error reading bookings:', error);
        return {};
    }
}

// Function to write bookings to file
function writeBookings(bookings) {
    try {
        fs.writeFileSync(bookingsFilePath, JSON.stringify(bookings, null, 2), 'utf8');
        return true;
    } catch (error) {
        console.error('Error writing bookings:', error);
        return false;
    }
}

// Handle GET requests - return all bookings
export function GET() {
    const bookings = readBookings();
    return json(bookings);
}

// Handle POST requests - add a new booking
export async function POST({ request }) {
    try {
        // Get booking data from request
        const { roomId, startTime, endTime } = await request.json();
        
        // Validate required fields
        if (!roomId || !startTime || !endTime) {
            return json({ error: 'Missing required fields: roomId, startTime, endTime' }, { status: 400 });
        }
        
        // Read current bookings
        const bookings = readBookings();
        
        // Initialize room bookings if it doesn't exist
        if (!bookings[roomId]) {
            bookings[roomId] = [];
        }
        
        // Add new booking
        bookings[roomId].push({ 
            startTime, 
            endTime,
            bookedAt: new Date().toISOString() 
        });
        
        // Save updated bookings
        if (writeBookings(bookings)) {
            return json({ success: true, message: 'Booking saved successfully' });
        } else {
            return json({ error: 'Failed to save booking' }, { status: 500 });
        }
    } catch (error) {
        console.error('Error processing booking:', error);
        return json({ error: 'Failed to process booking request' }, { status: 500 });
    }
} 