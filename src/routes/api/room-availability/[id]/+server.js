import { json } from '@sveltejs/kit';
import roomAvailability from '$lib/data/room_availability.json';

export async function GET({ params }) {
  const availability = roomAvailability[params.id] || [];
  return json(availability);
} 