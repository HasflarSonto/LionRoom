document.addEventListener("DOMContentLoaded", function () {
    const map = L.map("studySpaceMap").setView([40.8075, -73.9626], 15); // Columbia's coordinates

    // Load OpenStreetMap tiles (free alternative to Google Maps)
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    let markersLayer = L.layerGroup().addTo(map);

    // Function to fetch and display study spaces
    function loadStudySpaces() {
        fetch("/api/spaces")
            .then(response => response.json())
            .then(data => {
                markersLayer.clearLayers(); // Clear previous markers
                data.forEach(space => {
                    let marker = L.marker([space.location.lat, space.location.lng])
                        .bindPopup(`
                            <strong>${space.name}</strong><br>
                            Type: ${space.type}<br>
                            Availability: ${space.availability}<br>
                            <a href="/view/${space.id}">View Details</a>
                        `);
                    markersLayer.addLayer(marker);
                });
            })
            .catch(error => console.error("Error loading study spaces:", error));
    }

    // Load study spaces initially
    loadStudySpaces();

    // Handle filter application
    document.getElementById("applyMapFilters").addEventListener("click", function () {
        const typeFilter = document.getElementById("filterType").value;
        const availabilityFilter = document.getElementById("filterAvailability").value;

        fetch("/api/spaces")
            .then(response => response.json())
            .then(data => {
                let filteredSpaces = data.filter(space => {
                    return (
                        (typeFilter === "all" || space.type === typeFilter) &&
                        (availabilityFilter === "all" ||
                            (availabilityFilter === "available" && space.current_status === "Open") ||
                            (availabilityFilter === "reserved" && space.current_status === "Booked"))
                    );
                });

                markersLayer.clearLayers(); // Clear existing markers
                filteredSpaces.forEach(space => {
                    let statusClass = space.current_status === "Open" ? "text-success" : 
                                    space.current_status === "Booked" ? "text-danger" : "text-secondary";
                    let marker = L.marker([space.location.lat, space.location.lng])
                        .bindPopup(`
                            <strong>${space.name}</strong><br>
                            Type: ${space.type}<br>
                            Status: <span class="${statusClass}">${space.current_status}</span><br>
                            <a href="/view/${space.id}">View Details</a>
                        `);
                    markersLayer.addLayer(marker);
                });
            })
            .catch(error => console.error("Error filtering study spaces:", error));
    });

    // Add this after your map initialization
    map.on('click', function(e) {
        console.log(`Clicked coordinates: lat: ${e.latlng.lat}, lng: ${e.latlng.lng}`);
    });
});
