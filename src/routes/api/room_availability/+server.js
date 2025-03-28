import { json } from '@sveltejs/kit';

export async function GET() {
    try {
        const roomAvailability = await import('$lib/data/room_availability.json');
        return json(roomAvailability.default);
    } catch (error) {
        return new Response('Room availability data not found', { status: 404 });
    }
}