// Convert the availability data into an array of rooms
roomsData = Object.entries(availability)
  .map(([id, slots]) => ({
    id,
    name: roomNames[id],
    availability: slots || []  // Ensure slots is always an array
  })); 