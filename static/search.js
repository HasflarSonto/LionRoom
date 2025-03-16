document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const advancedSearchToggle = document.getElementById("advancedSearchToggle");
    const advancedSearchOptions = document.getElementById("advancedSearchOptions");
    const applyFilterButton = document.getElementById("applySearchFilters");

    // Default search (filters only available spaces)
    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value.toLowerCase();
            document.querySelectorAll(".search-result").forEach(item => {
                const name = item.dataset.name.toLowerCase();
                const availability = item.dataset.availability.toLowerCase();
                
                // Show only available spaces by default
                const matchesQuery = name.includes(query);
                const isAvailable = availability.includes("open");

                item.style.display = matchesQuery && isAvailable ? "block" : "none";
            });
        });
    }

    // Toggle advanced search filters
    if (advancedSearchToggle) {
        advancedSearchToggle.addEventListener("click", function () {
            advancedSearchOptions.classList.toggle("d-none"); // Show/hide filters
        });
    }

    // Apply advanced filters (time range & availability)
    if (applyFilterButton) {
        applyFilterButton.addEventListener("click", function () {
            const query = searchInput.value.toLowerCase();
            const startTime = document.getElementById("filterStartTime").value;
            const endTime = document.getElementById("filterEndTime").value;

            document.querySelectorAll(".search-result").forEach(item => {
                const name = item.dataset.name.toLowerCase();
                const availability = item.dataset.availability.toLowerCase();
                const openUntil = item.dataset.openuntil; // Expected format: "10 PM"

                let matchesQuery = name.includes(query);
                let isWithinTimeRange = true;

                // Convert time to comparable format (simple check)
                if (startTime && endTime) {
                    const openTime = parseInt(openUntil.replace(/\D/g, "")); // Extract hour
                    const startHour = parseInt(startTime.replace(/\D/g, ""));
                    const endHour = parseInt(endTime.replace(/\D/g, ""));

                    isWithinTimeRange = openTime >= startHour && openTime <= endHour;
                }

                item.style.display = matchesQuery && isWithinTimeRange ? "block" : "none";
            });
        });
    }
});
