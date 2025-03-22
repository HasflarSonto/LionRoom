<script>
  import Room from '$lib/components/Room.svelte';
  import { onMount, onDestroy } from 'svelte';

  let roomsData = [];
  let roomNames = {};
  let buildingsData = {};
  let classroomInfo = {};
  let viewMode = 'all'; // 'all' or 'buildings'
  let loadingError = null;
  let lastUpdateTime = null;
  let updateInterval;
  let isLoading = true;

  // Function to fetch all data
  async function fetchData() {
    isLoading = true;
    try {
      // Fetch all data in parallel
      const [availabilityRes, namesRes, buildingsRes, classroomInfoRes] = await Promise.all([
        fetch('/api/room_availability'),
        fetch('/api/room_names'),
        fetch('/src/lib/data/buildings.json'),
        fetch('/api/classroom_info')
      ]);

      const availability = await availabilityRes.json();
      roomNames = await namesRes.json();
      classroomInfo = await classroomInfoRes.json();

      // Map rooms with their info
      roomsData = Object.entries(availability)
        .map(([id, timeRanges]) => {
          const name = roomNames[id];
          return {
            id,
            name,
            availability: timeRanges || [],
            // Look up room info using the room name as the key
            info: name ? classroomInfo[name.toLowerCase()] : null
          };
        })
        .sort((a, b) => a.name?.localeCompare(b.name) || a.id.localeCompare(b.id));
        
      try {
        if (buildingsRes.ok) {
          buildingsData = await buildingsRes.json();
        } else {
          throw new Error(`Failed to fetch buildings data: ${buildingsRes.status}`);
        }
      } catch (buildingError) {
        console.error('Error fetching buildings data:', buildingError);
        loadingError = `Error loading buildings data: ${buildingError.message}. Using 'All' view by default.`;
        viewMode = 'all'; // Fallback to all view if buildings data fails
      }
      
      // Check for last update time
      try {
        const updateRes = await fetch('/src/lib/data/last_update.json');
        if (updateRes.ok) {
          const updateData = await updateRes.json();
          lastUpdateTime = new Date(updateData.timestamp);
        }
      } catch (e) {
        console.log('No update timestamp available');
      }
      
      loadingError = null;
    } catch (error) {
      console.error('Error fetching room data:', error);
      loadingError = `Error loading room data: ${error.message}`;
    } finally {
      isLoading = false;
    }
  }
  
  // Check for updates function
  async function checkForUpdates() {
    try {
      const response = await fetch('/src/lib/data/last_update.json');
      if (response.ok) {
        const data = await response.json();
        const newUpdateTime = new Date(data.timestamp);
        
        // If we have a new update and it's different from our current data
        if (!lastUpdateTime || newUpdateTime > lastUpdateTime) {
          console.log('New data available, refreshing...');
          lastUpdateTime = newUpdateTime;
          await fetchData();
        }
      }
    } catch (error) {
      console.error('Error checking for updates:', error);
    }
  }

  onMount(async () => {
    // Initial data fetch
    await fetchData();
    
    // Set up polling every minute to check for updates
    updateInterval = setInterval(checkForUpdates, 60000);
  });
  
  onDestroy(() => {
    // Clean up interval on component destroy
    if (updateInterval) clearInterval(updateInterval);
  });

  function setViewMode(mode) {
    viewMode = mode;
  }

  // Group rooms by building
  function getRoomsByBuilding() {
    const roomsByBuilding = {};
    
    if (!buildingsData || Object.keys(buildingsData).length === 0) {
      return { "All Rooms": roomsData };
    }
    
    // Initialize buildings with empty arrays
    Object.keys(buildingsData).forEach(building => {
      roomsByBuilding[building] = [];
    });
    
    // Populate rooms into their respective buildings
    roomsData.forEach(room => {
      let found = false;
      // Find which building this room belongs to
      for (const [building, rooms] of Object.entries(buildingsData)) {
        if (room.id in rooms) {
          if (!roomsByBuilding[building]) roomsByBuilding[building] = [];
          roomsByBuilding[building].push(room);
          found = true;
          break;
        }
      }
      
      // If room wasn't found in any building, add to Miscellaneous
      if (!found) {
        if (!roomsByBuilding["Miscellaneous"]) roomsByBuilding["Miscellaneous"] = [];
        roomsByBuilding["Miscellaneous"].push(room);
      }
    });
    
    return roomsByBuilding;
  }
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
</svelte:head>

<div class="container">
  <header class="header">
    <a href="/">Lion Room &#129409;</a>
    {#if lastUpdateTime}
      <div class="last-update">
        Last updated: {lastUpdateTime.toLocaleTimeString()}
      </div>
    {/if}
  </header>
  
  {#if loadingError}
    <div class="error-message">
      {loadingError}
    </div>
  {/if}
  
  <div class="view-toggle">
    <button 
      class:active={viewMode === 'all'} 
      on:click={() => setViewMode('all')}
    >
      All Rooms
    </button>
    <button 
      class:active={viewMode === 'buildings'} 
      on:click={() => setViewMode('buildings')}
      disabled={!buildingsData || Object.keys(buildingsData).length === 0}
    >
      By Building
    </button>
  </div>
  
  {#if isLoading && roomsData.length === 0}
    <div class="loading">Loading room data...</div>
  {:else if roomsData.length === 0}
    <div class="loading">No room data available</div>
  {:else if viewMode === 'all'}
    <div class="rooms-container">
      {#each roomsData as room (room.id)}
        <Room 
          roomId={room.id}
          roomName={room.name}
          availability={room.availability}
          roomInfo={room.info}
        />
      {/each}
    </div>
  {:else}
    <div class="buildings-container">
      {#each Object.entries(getRoomsByBuilding()) as [building, rooms] (building)}
        {#if rooms.length > 0}
          <div class="building-section">
            <h2>{building}</h2>
            <div class="rooms-container">
              {#each rooms as room (room.id)}
                <Room 
                  roomId={room.id}
                  roomName={room.name}
                  availability={room.availability}
                  roomInfo={room.info}
                />
              {/each}
            </div>
          </div>
        {/if}
      {/each}
    </div>
  {/if}
</div>

<style>
  :global(body) {
    font-family: 'Poppins', sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f8f8f8;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .header {
    text-align: center;
    padding: 2rem 0 0.5rem;
    margin-bottom: 1rem;
    font-size: 2.5rem;
    font-weight: 700;
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .header a {
    color: #1e3a8a;
    text-decoration: none;
  }
  
  .last-update {
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.5rem;
    font-weight: 400;
  }

  h2 {
    font-size: 1.5rem;
    color: #1e3a8a;
    margin: 1.5rem 0 0.5rem 0;
    border-bottom: 2px solid #eee;
    padding-bottom: 0.5rem;
    font-weight: 600;
  }

  .view-toggle {
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
    gap: 1rem;
  }

  .view-toggle button {
    padding: 0.5rem 1.5rem;
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
  }

  .view-toggle button:hover:not(:disabled) {
    background-color: #e9ecef;
  }

  .view-toggle button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .view-toggle button.active {
    background-color: #1e3a8a;
    color: white;
    border-color: #1e3a8a;
  }

  .rooms-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .buildings-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .building-section {
    margin-bottom: 1rem;
  }
  
  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-style: italic;
  }
  
  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid #f5c6cb;
    border-radius: 0.25rem;
  }
</style>