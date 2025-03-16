document.addEventListener("DOMContentLoaded", function () {
    // Get the map container
    const mapElement = document.getElementById("map");
    
    // Get location data from data attributes
    const lat = parseFloat(mapElement.dataset.lat);
    const lng = parseFloat(mapElement.dataset.lng);
    const spaceName = mapElement.dataset.name;
    
    // Initialize the map
    const map = L.map("map").setView([lat, lng], 16);

    // Add the OpenStreetMap tiles
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    // Add a marker for this location
    L.marker([lat, lng])
        .bindPopup(`<strong>${spaceName}</strong>`)
        .addTo(map);
}); 