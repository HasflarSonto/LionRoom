import { json } from '@sveltejs/kit';
import classroomInfo from '$lib/data/classroom_info.json';

export async function GET() {
    return json(classroomInfo);
}