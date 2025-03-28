import { json } from '@sveltejs/kit';
import classroomInfo from '$lib/data/classroom_info.json';

export async function GET({ params }) {
  const roomInfo = classroomInfo[params.id];
  if (!roomInfo) {
    return new Response('Room not found', { status: 404 });
  }
  return json(roomInfo);
} 