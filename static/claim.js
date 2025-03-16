document.addEventListener("DOMContentLoaded", function () {
    const claimBtn = document.getElementById("claim-btn");
    
    if (claimBtn) {
        claimBtn.addEventListener("click", function () {
            const spaceId = this.dataset.spaceId;
            const claimStatus = this.dataset.claimed === "true" ? false : true;

            fetch(`/claim/${spaceId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({ claimed: claimStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update button state
                    this.dataset.claimed = claimStatus.toString();
                    this.textContent = claimStatus ? "Unclaim This Space" : "Claim This Space";
                    this.className = `btn ${claimStatus ? 'btn-warning' : 'btn-success'}`;
                    
                    // Update badge
                    const claimBadge = document.querySelector('.badge.bg-warning, .badge.bg-info');
                    if (claimBadge) {
                        claimBadge.textContent = claimStatus ? "Claimed" : "Unclaimed";
                        claimBadge.className = `badge ${claimStatus ? 'bg-warning' : 'bg-info'}`;
                    }
                }
            })
            .catch(error => console.error("Error:", error));
        });
    }
});
