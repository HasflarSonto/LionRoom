document.addEventListener('DOMContentLoaded', function() {
    // Fetch both room availability and room names
    Promise.all([
        fetch('/get_room_availability'),
        fetch('/get_room_names')  // You'll need to create this endpoint
    ])
    .then(responses => Promise.all(responses.map(res => res.json())))
    .then(([availabilityData, roomNames]) => createTimeline(availabilityData, roomNames));
});

function createTimeline(roomData, roomNames) {
    const timeMarkers = document.querySelector('.time-markers');
    const roomsContainer = document.querySelector('.rooms-container');

    // Add time markers
    for (let hour = 0; hour < 24; hour++) {
        const marker = document.createElement('div');
        marker.className = 'time-marker';
        marker.style.left = `${hour * 60 + 200}px`; // Add 200px offset for room header
        marker.textContent = formatTime(hour * 60);
        timeMarkers.appendChild(marker);
    }

    // Add room timelines
    for (const [roomId, availability] of Object.entries(roomData)) {
        // Skip rooms with no availability data
        if (!availability || availability.length === 0) continue;

        const roomTimeline = document.createElement('div');
        roomTimeline.className = 'room-timeline';

        // Add room header with room name instead of ID
        const header = document.createElement('div');
        header.className = 'room-header';
        header.textContent = roomNames[roomId] || `Room ${roomId}`;
        roomTimeline.appendChild(header);

        // Add available slots
        availability.forEach(slot => {
            const [startTime, endTime] = slot;
            const startMinutes = timeToMinutes(startTime);
            const endMinutes = timeToMinutes(endTime);
            
            const availableSlot = document.createElement('div');
            availableSlot.className = 'available-slot';
            availableSlot.style.left = `${startMinutes + 200}px`; // Add 200px offset for room header
            availableSlot.style.width = `${endMinutes - startMinutes}px`;
            availableSlot.textContent = `${startTime} - ${endTime}`;
            roomTimeline.appendChild(availableSlot);
        });

        roomsContainer.appendChild(roomTimeline);
    }

    // Add current time marker
    updateCurrentTimeMarker();
    setInterval(updateCurrentTimeMarker, 60000); // Update every minute
}

function timeToMinutes(timeStr) {
    const [time, period] = timeStr.split(' ');
    let [hours, minutes] = time.split(':').map(Number);
    
    if (period === 'PM' && hours !== 12) hours += 12;
    if (period === 'AM' && hours === 12) hours = 0;
    
    return hours * 60 + minutes;
}

function formatTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    const period = hours >= 12 ? 'PM' : 'AM';
    const displayHours = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;
    return `${displayHours}:${mins.toString().padStart(2, '0')} ${period}`;
}

function updateCurrentTimeMarker() {
    const now = new Date();
    const minutes = now.getHours() * 60 + now.getMinutes();
    
    const existingMarker = document.querySelector('.current-time-marker');
    if (existingMarker) existingMarker.remove();

    const marker = document.createElement('div');
    marker.className = 'current-time-marker';
    marker.style.left = `${minutes + 200}px`; // Add 200px offset for room header
    document.querySelector('.timeline-container').appendChild(marker);
}
