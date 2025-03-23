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
  
  // Add a new state for search query
  let searchQuery = '';
  
  // Update the filters object to include search
  let filters = {
    searchQuery: '',           // Add search query to filters
    showCurrentlyAvailable: true,
    hasChalkboard: false,
    hasWhiteboard: false,
    minCapacity: '',
    minSharedTables: '',
    roomType: 'any',
    seatingStyle: 'any',
    tableStyle: 'any'
  };
  
  // Filter options
  const roomTypes = ['any', 'seminar', 'classroom', 'lecture hall', 'auditorium', 'computer lab'];
  const seatingStyles = ['any', 'fixed chairs', 'moveable chairs'];
  const tableStyles = ['any', 'moveable tables', 'fixed tables', 'moveable tablets', 'fixed tablets'];

  // Add a state variable to track if filters are expanded
  let isFiltersExpanded = false;
  
  // Function to toggle filters visibility
  function toggleFilters() {
    isFiltersExpanded = !isFiltersExpanded;
  }

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

      // Debug logging
      console.log('Room availability entries:', Object.keys(availability).length);
      console.log('Room names entries:', Object.keys(roomNames).length);
      console.log('Classroom info entries:', Object.keys(classroomInfo).length);
      
      // Sample data checks
      console.log('Sample availability entry:', Object.entries(availability)[0]);
      console.log('Sample room name entry:', Object.entries(roomNames)[0]);
      console.log('Sample classroom info entry:', Object.entries(classroomInfo)[0]);

      // Add this before the map operation to identify missing room names
      const missingNames = Object.keys(availability).filter(id => !roomNames[id]);
      console.log('Room IDs missing from roomNames:', missingNames);

      // Map rooms with their info
      roomsData = Object.entries(availability)
        .map(([id, timeRanges]) => {
          const name = roomNames[id];
          const info = name ? classroomInfo[name.toLowerCase()] : null;
          
          // Debug specific rooms that don't match up
          if (name && !info) {
            console.log(`Missing info for room: ${name} (ID: ${id})`);
          }
          
          return {
            id,
            name,
            availability: timeRanges || [],
            info: info
          };
        })
        // Filter out rooms without names in the room_names.json file
        .filter(room => room.name)
        .sort((a, b) => a.name?.localeCompare(b.name) || a.id.localeCompare(b.id));
      
      console.log('Total processed rooms:', roomsData.length);
      
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
  
  // Function to check for updates (missing in your code)
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
  
  // Add the missing timeStringToMinutes function
  function timeStringToMinutes(timeStr) {
    try {
      if (!timeStr || typeof timeStr !== 'string') {
        console.error('Invalid time string:', timeStr);
        return 0;
      }
      
      const parts = timeStr.split(' ');
      if (parts.length !== 2) {
        console.error('Time string has unexpected format:', timeStr);
        return 0;
      }
      
      const [time, period] = parts;
      const timeParts = time.split(':');
      if (timeParts.length !== 2) {
        console.error('Time part has unexpected format:', time);
        return 0;
      }
      
      const hours = parseInt(timeParts[0]);
      const minutes = parseInt(timeParts[1]);
      
      if (isNaN(hours) || isNaN(minutes)) {
        console.error('Hours or minutes is not a number:', hours, minutes);
        return 0;
      }
      
      let totalMinutes = minutes;
      
      if (period === 'PM' && hours !== 12) {
        totalMinutes += (hours + 12) * 60;
      } else if (period === 'AM' && hours === 12) {
        totalMinutes += 0; // 12 AM is 0 hours
      } else {
        totalMinutes += hours * 60;
      }
      
      return totalMinutes;
    } catch (error) {
      console.error('Error in timeStringToMinutes:', error, timeStr);
      return 0;
    }
  }

  // Update the filterRooms function to include search functionality
  function filterRooms(rooms) {
    console.log('Applying filters:', JSON.stringify(filters));
    
    // Return early if rooms is empty or not an array
    if (!rooms || !Array.isArray(rooms) || rooms.length === 0) {
      console.log('No rooms to filter');
      return [];
    }
    
    try {
      const filteredRooms = rooms.filter(room => {
        // Skip rooms with no data
        if (!room) return false;
        
        // Search filter - case insensitive search in room name
        if (filters.searchQuery && filters.searchQuery.trim() !== '') {
          const query = filters.searchQuery.toLowerCase().trim();
          // If room has no name or name doesn't include search query, filter it out
          if (!room.name || !room.name.toLowerCase().includes(query)) {
            return false;
          }
        }
        
        const info = room.info || {};
        
        // Filter by current availability
        if (filters.showCurrentlyAvailable) {
          try {
            const now = new Date();
            const currentHour = now.getHours();
            const currentMinutes = now.getMinutes();
            const currentTimeInMinutes = currentHour * 60 + currentMinutes;
            
            console.log(`Current time: ${currentHour}:${currentMinutes} (${currentTimeInMinutes} minutes)`);
            
            // Check if current time falls within any availability window
            let isCurrentlyAvailable = false;
            
            if (Array.isArray(room.availability) && room.availability.length > 0) {
              for (const timeRange of room.availability) {
                if (!Array.isArray(timeRange) || timeRange.length !== 2) continue;
                
                const [start, end] = timeRange;
                if (!start || !end) continue;
                
                const startMinutes = timeStringToMinutes(start);
                let endMinutes = timeStringToMinutes(end);
                
                // Special case handling for end of day
                if (end === "12:00 AM" || end === "12:00 PM") {
                  endMinutes = 24 * 60; // End of day
                }
                
                console.log(`Room ${room.name} time range: ${start} (${startMinutes}) - ${end} (${endMinutes})`);
                
                if (currentTimeInMinutes >= startMinutes && currentTimeInMinutes < endMinutes) {
                  isCurrentlyAvailable = true;
                  console.log(`Room ${room.name} is currently available`);
                  break;
                }
              }
            }
            
            if (!isCurrentlyAvailable) {
              console.log(`Room ${room.name} is NOT currently available`);
              return false;
            }
          } catch (error) {
            console.error('Error checking availability for room:', room.name, error);
            return false;
          }
        }
        
        // Skip rooms with no info if we're filtering by room properties
        if (!info && (
          filters.hasChalkboard || 
          filters.hasWhiteboard || 
          filters.minCapacity || 
          filters.minSharedTables || 
          filters.roomType !== 'any' || 
          filters.seatingStyle !== 'any' || 
          filters.tableStyle !== 'any'
        )) {
          return false;
        }
        
        // If we got this far and there's no info, return true
        if (!info) return true;
        
        // Filter by board type
        if (filters.hasChalkboard && info.board_type !== 'chalkboard') return false;
        if (filters.hasWhiteboard && info.board_type !== 'whiteboard') return false;
        
        // Filter by capacity
        if (filters.minCapacity && filters.minCapacity.trim() !== '') {
          const minCapacity = parseInt(filters.minCapacity);
          if (!isNaN(minCapacity)) {
            // Make sure info.capacity exists and is a number
            if (!info.capacity || parseInt(info.capacity) < minCapacity) {
              return false;
            }
          }
        }
        
        // Filter by shared tables
        if (filters.minSharedTables && filters.minSharedTables.trim() !== '') {
          const minSharedTables = parseInt(filters.minSharedTables);
          if (!isNaN(minSharedTables)) {
            // Make sure info.shared_tables exists and is a number
            if (info.shared_tables === undefined || 
                info.shared_tables === null || 
                parseInt(info.shared_tables) < minSharedTables) {
              return false;
            }
          }
        }
        
        // Filter by room type (case-insensitive)
        if (filters.roomType !== 'any') {
          if (!info.room_type || 
              info.room_type.toLowerCase() !== filters.roomType.toLowerCase()) {
            return false;
          }
        }
        
        // Filter by seating style (case-insensitive and partial match)
        if (filters.seatingStyle !== 'any') {
          if (!info.seating_style || 
              !info.seating_style.toLowerCase().includes(filters.seatingStyle.toLowerCase())) {
            return false;
          }
        }
        
        // Filter by table style (case-insensitive and partial match)
        if (filters.tableStyle !== 'any') {
          if (!info.table_style || 
              !info.table_style.toLowerCase().includes(filters.tableStyle.toLowerCase())) {
            return false;
          }
        }
        
        // If all filters passed, include this room
        return true;
      });
      
      console.log(`Filtered ${rooms.length} rooms down to ${filteredRooms.length} rooms`);
      return filteredRooms;
    } catch (error) {
      console.error('Error in filterRooms:', error);
      return [];
    }
  }

  // Add a helper function to check availability for debugging
  function checkRoomAvailability(room) {
    if (!room || !Array.isArray(room.availability)) return false;
    
    const now = new Date();
    const currentHour = now.getHours();
    const currentMinutes = now.getMinutes();
    const currentTimeInMinutes = currentHour * 60 + currentMinutes;
    
    for (const timeRange of room.availability) {
      if (!Array.isArray(timeRange) || timeRange.length !== 2) continue;
      
      const [start, end] = timeRange;
      if (!start || !end) continue;
      
      const startMinutes = timeStringToMinutes(start);
      let endMinutes = timeStringToMinutes(end);
      
      // Special case handling for end of day
      if (end === "12:00 AM" || end === "12:00 PM") {
        endMinutes = 24 * 60; // End of day
      }
      
      if (currentTimeInMinutes >= startMinutes && currentTimeInMinutes < endMinutes) {
        return true;
      }
    }
    
    return false;
  }
  
  // Add a function to trigger re-filtering
  function applyFilters() {
    console.log('Manually applying filters');
    filteredRoomsData = filterRooms(roomsData);
  }
  
  // Add observer to watch filter changes
  let lastFilterState = JSON.stringify(filters);
  function checkFiltersChanged() {
    const currentState = JSON.stringify(filters);
    if (currentState !== lastFilterState) {
      console.log('Filters changed, reapplying filters');
      lastFilterState = currentState;
      applyFilters();
    }
  }
  
  // Set up an interval to check for filter changes (as a backup in case reactivity doesn't work)
  onMount(() => {
    const filterCheckInterval = setInterval(checkFiltersChanged, 500);
    return () => clearInterval(filterCheckInterval);
  });
  
  // Make update helpers force a filter recalculation
  function updateCheckbox(key, event) {
    filters[key] = event.target.checked;
    filters = {...filters}; // Create a new object to ensure reactivity
    console.log(`Updated ${key} to ${filters[key]}`);
    applyFilters(); // Force refiltering
  }
  
  function updateInputValue(key, event) {
    filters[key] = event.target.value;
    filters = {...filters}; // Create a new object to ensure reactivity
    console.log(`Updated ${key} to ${filters[key]}`);
    applyFilters(); // Force refiltering
  }
  
  function updateSelectValue(key, event) {
    filters[key] = event.target.value;
    filters = {...filters}; // Create a new object to ensure reactivity
    console.log(`Updated ${key} to ${filters[key]}`);
    applyFilters(); // Force refiltering
  }
  
  // Update the reset function to clear search as well
  function resetFilters() {
    filters = {
      searchQuery: '',         // Reset search query
      showCurrentlyAvailable: true,
      hasChalkboard: false,
      hasWhiteboard: false,
      minCapacity: '',
      minSharedTables: '',
      roomType: 'any',
      seatingStyle: 'any',
      tableStyle: 'any'
    };
    console.log('Filters reset');
    applyFilters(); // Force refiltering
  }
  
  // Make filterRooms reactive to filter changes
  $: filteredRoomsData = filterRooms(roomsData);
  
  // Update the hasActiveFilters check to include search
  $: hasActiveFilters = 
    filters.searchQuery ||
    filters.showCurrentlyAvailable || 
    filters.hasChalkboard || 
    filters.hasWhiteboard || 
    filters.minCapacity || 
    filters.minSharedTables || 
    filters.roomType !== 'any' || 
    filters.seatingStyle !== 'any' || 
    filters.tableStyle !== 'any';

  // Add a search handler function
  function handleSearch(event) {
    filters.searchQuery = event.target.value;
    filters = {...filters}; // Create a new object to ensure reactivity
    console.log(`Updated search query to: "${filters.searchQuery}"`);
    applyFilters(); // Force refiltering
  }

  onMount(async () => {
    // Initial data fetch
    await fetchData();
    
    // Apply filters immediately after loading data (will use the defaults including "Currently Available")
    applyFilters();
    
    // Debug availability
    setTimeout(() => {
      if (roomsData.length > 0) {
        console.log('Checking availability for sample rooms:');
        roomsData.slice(0, 5).forEach(room => {
          const isAvailable = checkRoomAvailability(room);
          console.log(`Room ${room.name}: ${isAvailable ? 'Available' : 'Not Available'}`);
          console.log(`Availability windows:`, room.availability);
        });
      }
    }, 2000);
    
    // Set up polling every minute to check for updates
    updateInterval = setInterval(checkForUpdates, 60000);
  });
  
  onDestroy(() => {
    // Clean up interval on component destroy
    if (updateInterval) clearInterval(updateInterval);
  });

  function setViewMode(mode, isChecked) {
    if (isChecked) {
      viewMode = mode;
    } else if (viewMode === mode) {
      viewMode = 'all';
    }
  }

  // Group rooms by building (modified to use filtered rooms)
  function getRoomsByBuilding() {
    const roomsByBuilding = {};
    
    if (!buildingsData || Object.keys(buildingsData).length === 0) {
      return { "All Rooms": filteredRoomsData };
    }
    
    // Initialize buildings with empty arrays
    Object.keys(buildingsData).forEach(building => {
      roomsByBuilding[building] = [];
    });
    
    // Populate rooms into their respective buildings
    filteredRoomsData.forEach(room => {
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

  function getPhotoUrl(roomId, roomName) {
    if (!roomName) return null;

    const parts = roomName.split(' ');
    if (parts.length < 2) return null;

    let building = parts.slice(0, parts.length-1).join('_').toLowerCase();
    let roomNumber = parts[parts.length-1];

    const photoPath = `/src/lib/data/photos/${building}_${roomNumber}_1`;
    return `${photoPath}.jpg`;
  }
</script>

<svelte:head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
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
  
  <!-- Add search bar above everything -->
  <div class="search-container">
    <div class="search-input-container">
      <i class="fas fa-search search-icon"></i>
      <input 
        type="text" 
        placeholder="Search for a room..." 
        class="search-input" 
        value={filters.searchQuery}
        on:input={handleSearch}
      />
      {#if filters.searchQuery}
        <button class="search-clear-button" on:click={() => {
          filters.searchQuery = '';
          filters = {...filters};
          applyFilters();
        }}>
          <i class="fas fa-times"></i>
        </button>
      {/if}
    </div>
  </div>
  
  <!-- Make filters panel expandable/collapsible -->
  <div class="filters-panel">
    <div class="filters-header" on:click={toggleFilters}>
      <h3>
        <div class="filters-title">
          <i class="fas fa-filter"></i> Filters
          <span class="filter-count">{filteredRoomsData.length} room{filteredRoomsData.length !== 1 ? 's' : ''} found</span>
        </div>
        <div class="filters-actions">
          {#if Object.values(filters).some(v => v !== false && v !== '' && v !== 'any')}
            <button class="reset-button" on:click={(e) => {
              e.stopPropagation(); // Prevent toggling when clicking reset
              resetFilters();
            }}>
              <i class="fas fa-times"></i> Reset
            </button>
          {/if}
          <i class={`fas ${isFiltersExpanded ? 'fa-chevron-up' : 'fa-chevron-down'} filter-toggle-icon`}></i>
        </div>
      </h3>
    </div>
    
    {#if isFiltersExpanded}
      <div class="filters-content">
        <!-- Add the view mode buttons as the first section -->
        <div class="filter-section view-mode-section">
          <div class="filter-group">
            <label>View Mode</label>
            <div class="view-toggle-options">
              <div class="view-toggle-row">
                <label class="radio-label">
                  <input 
                    type="radio" 
                    name="viewMode"
                    checked={viewMode === 'all'} 
                    on:change={(e) => {
                      e.stopPropagation();
                      if (e.target.checked) {
                        setViewMode('all', true);
                      }
                    }}
                  />
                  <span class="radio-circle"></span>
                  <span class="radio-text">All Rooms</span>
                </label>
                
                <label class="radio-label">
                  <input 
                    type="radio" 
                    name="viewMode"
                    checked={viewMode === 'buildings'} 
                    disabled={!buildingsData || Object.keys(buildingsData).length === 0}
                    on:change={(e) => {
                      e.stopPropagation();
                      setViewMode('buildings', e.target.checked);
                    }}
                  />
                  <span class="radio-circle"></span>
                  <span class="radio-text">By Building</span>
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Existing filter sections -->
        <div class="filter-section">
          <div class="filter-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                checked={filters.showCurrentlyAvailable} 
                on:change={(e) => updateCheckbox('showCurrentlyAvailable', e)}
              >
              <span>Currently Available</span>
            </label>
          </div>
          
          <div class="filter-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                checked={filters.hasChalkboard} 
                on:change={(e) => updateCheckbox('hasChalkboard', e)}
              >
              <span>Has Chalkboard</span>
            </label>
          </div>
          
          <div class="filter-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                checked={filters.hasWhiteboard} 
                on:change={(e) => updateCheckbox('hasWhiteboard', e)}
              >
              <span>Has Whiteboard</span>
            </label>
          </div>
        </div>
        
        <!-- Rest of the existing filter sections -->
        <div class="filter-section">
          <div class="filter-group">
            <label for="minCapacity">Minimum Capacity</label>
            <input 
              type="number" 
              id="minCapacity" 
              value={filters.minCapacity} 
              on:input={(e) => updateInputValue('minCapacity', e)}
              placeholder="Min seats"
              min="0"
            >
          </div>
          
          <div class="filter-group">
            <label for="minSharedTables">Minimum Shared Tables</label>
            <input 
              type="number" 
              id="minSharedTables" 
              value={filters.minSharedTables} 
              on:input={(e) => updateInputValue('minSharedTables', e)}
              placeholder="Min tables"
              min="0"
            >
          </div>
        </div>
        
        <div class="filter-section">
          <div class="filter-group">
            <label for="roomType">Room Type</label>
            <select 
              id="roomType" 
              value={filters.roomType}
              on:change={(e) => updateSelectValue('roomType', e)}
            >
              {#each roomTypes as type}
                <option value={type}>{type === 'any' ? 'Any Type' : type.charAt(0).toUpperCase() + type.slice(1)}</option>
              {/each}
            </select>
          </div>
          
          <div class="filter-group">
            <label for="seatingStyle">Seating Style</label>
            <select 
              id="seatingStyle" 
              value={filters.seatingStyle}
              on:change={(e) => updateSelectValue('seatingStyle', e)}
            >
              {#each seatingStyles as style}
                <option value={style}>{style === 'any' ? 'Any Style' : style.charAt(0).toUpperCase() + style.slice(1)}</option>
              {/each}
            </select>
          </div>
          
          <div class="filter-group">
            <label for="tableStyle">Table Style</label>
            <select 
              id="tableStyle" 
              value={filters.tableStyle}
              on:change={(e) => updateSelectValue('tableStyle', e)}
            >
              {#each tableStyles as style}
                <option value={style}>{style === 'any' ? 'Any Style' : style.charAt(0).toUpperCase() + style.slice(1)}</option>
              {/each}
            </select>
          </div>
        </div>
      </div>
    {/if}
  </div>
  
  <!-- Rest of the content remains the same -->
  {#if isLoading && roomsData.length === 0}
    <div class="loading">Loading room data...</div>
  {:else if filteredRoomsData.length === 0}
    <div class="no-results">
      <i class="fas fa-search"></i>
      <p>No rooms match your filters</p>
      <button class="reset-button" on:click={resetFilters}>Clear Filters</button>
    </div>
  {:else if viewMode === 'all'}
    <div class="rooms-container">
      {#each filteredRoomsData as room (room.id)}
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

  .view-toggle-options {
    margin-top: 0.5rem;
  }
  
  .view-toggle-row {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
  }
  
  .radio-label {
    display: flex;
    align-items: center;
    position: relative;
    padding: 0.5rem 0;
    cursor: pointer;
    user-select: none;
    margin-right: 1rem;
  }
  
  .radio-label input[type="radio"] {
    position: absolute;
    opacity: 0;
    cursor: pointer;
    height: 0;
    width: 0;
  }
  
  .radio-circle {
    position: relative;
    display: inline-block;
    width: 18px;
    height: 18px;
    background-color: #f8f9fa;
    border: 2px solid #ddd;
    border-radius: 50%;
    margin-right: 0.5rem;
    transition: all 0.2s ease;
  }
  
  .radio-label:hover .radio-circle {
    border-color: #c5c9cd;
  }
  
  .radio-label input[type="radio"]:checked + .radio-circle {
    background-color: #1e3a8a;
    border-color: #1e3a8a;
  }
  
  .radio-label input[type="radio"]:checked + .radio-circle:after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: white;
  }
  
  .radio-label input[type="radio"]:disabled + .radio-circle {
    background-color: #f1f3f5;
    border-color: #e1e4e8;
    cursor: not-allowed;
  }
  
  .radio-text {
    font-weight: 500;
    font-size: 0.95rem;
    color: #333;
  }
  
  .radio-label input[type="radio"]:disabled ~ .radio-text {
    color: #999;
    cursor: not-allowed;
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

  .filters-panel {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
    overflow: hidden;
  }

  .filters-header {
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .filters-header:hover {
    background: #f1f3f5;
  }

  .filters-header h3 {
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #1e3a8a;
    font-size: 1.1rem;
  }

  .filters-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .filter-count {
    font-size: 0.8rem;
    color: #666;
    background: #e9ecef;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    margin-left: 0.5rem;
    font-weight: normal;
  }

  .filters-actions {
    display: flex;
    align-items: center;
    gap: 0.8rem;
  }

  .filter-toggle-icon {
    color: #666;
    font-size: 0.9rem;
  }

  .filters-content {
    padding: 1.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
  }

  .filter-section {
    flex: 1;
    min-width: 300px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .checkbox-group {
    flex-direction: row;
    align-items: center;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    user-select: none;
  }

  .checkbox-label input {
    cursor: pointer;
    width: 18px;
    height: 18px;
  }

  .filter-group label {
    font-size: 0.9rem;
    font-weight: 500;
    color: #333;
  }

  .filter-group input[type="number"] {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: 'Poppins', sans-serif;
  }

  .filter-group select {
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: 'Poppins', sans-serif;
    background: white;
  }

  .reset-button {
    background: #edf2ff;
    color: #3b5bdb;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.3rem;
  }

  .reset-button:hover {
    background: #dbe4ff;
  }
  
  .no-results {
    text-align: center;
    padding: 3rem 1rem;
    color: #666;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }
  
  .no-results i {
    font-size: 2rem;
    color: #ddd;
  }

  .no-results p {
    margin: 0;
    font-size: 1.1rem;
  }
  
  .no-results .reset-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  /* Make filters responsive */
  @media (max-width: 768px) {
    .filters-content {
      flex-direction: column;
      gap: 1rem;
    }
    
    .filter-section {
      min-width: auto;
    }
  }

  /* Add styles for the search bar */
  .search-container {
    margin-bottom: 1.5rem;
  }
  
  .search-input-container {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .search-icon {
    position: absolute;
    left: 1rem;
    color: #999;
  }
  
  .search-input {
    padding: 0.8rem 1rem 0.8rem 2.5rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-family: 'Poppins', sans-serif;
    font-size: 1rem;
    width: 100%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 2px 12px rgba(59,130,246,0.1);
  }
  
  .search-clear-button {
    position: absolute;
    right: 1rem;
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    padding: 0.3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background-color 0.2s;
  }
  
  .search-clear-button:hover {
    background-color: #f0f0f0;
    color: #666;
  }
  
  /* Responsive search bar */
  @media (max-width: 768px) {
    .search-input {
      font-size: 0.9rem;
      padding: 0.7rem 1rem 0.7rem 2.3rem;
    }
  }
</style>