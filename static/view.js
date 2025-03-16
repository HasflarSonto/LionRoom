document.addEventListener("DOMContentLoaded", function() {
    function updateStatus() {
        const spaceId = document.querySelector('[data-space-id]').dataset.spaceId;
        
        fetch(`/api/space-status/${spaceId}`)
            .then(response => response.json())
            .then(data => {
                // Update current status text
                const statusSpan = document.getElementById('current-status');
                if (statusSpan) {
                    statusSpan.textContent = data.status;
                }

                // Update status badge
                const statusBadge = document.getElementById('status-badge');
                if (statusBadge) {
                    statusBadge.textContent = data.status;
                    let badgeClass = 'badge ';
                    switch(data.status) {
                        case 'Booked':
                            badgeClass += 'bg-danger';
                            break;
                        case 'Closed':
                            badgeClass += 'bg-secondary';
                            break;
                        default:
                            badgeClass += 'bg-success';
                    }
                    statusBadge.className = `${badgeClass} me-2`;
                }
            })
            .catch(error => console.error('Error updating status:', error));
    }

    // Update status immediately and then every minute
    updateStatus();
    setInterval(updateStatus, 60000);
});