import { json } from '@sveltejs/kit';

export async function GET() {
    try {
        const buildings = await import('$lib/data/buildings.json');
        return json(buildings.default);
    } catch (error) {
        return new Response('Buildings data not found', { status: 404 });
    }
} 