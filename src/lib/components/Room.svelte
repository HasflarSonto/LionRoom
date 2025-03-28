<script>
  import { onMount } from 'svelte';
  export let roomId;
  export let availability;
  export let roomName;
  export let roomInfo;

  // Create an array of 24 hours
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Format time for display (12-hour format)
  function formatTime(hour) {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    return `${displayHour}:00 ${period}`;
  }

  // Convert time string (HH:mm AM/PM) to minutes since midnight
  function timeStringToMinutes(timeStr) {
    const [time, period] = timeStr.split(' ');
    const [hours, minutes] = time.split(':').map(Number);
    
    let totalMinutes = minutes;
    
    if (period === 'PM' && hours !== 12) {
      totalMinutes += (hours + 12) * 60;
    } else if (period === 'AM' && hours === 12) {
      totalMinutes += 0;
    } else {
      totalMinutes += hours * 60;
    }
    
    return totalMinutes;
  }

  // Calculate availability for a specific hour
  function getHourAvailability(hour) {
    // Convert hour to minutes for comparison
    const hourStartMinutes = hour * 60;
    const hourEndMinutes = (hour + 1) * 60;

    // If there's no availability data or it's empty, room is unavailable
    if (!Array.isArray(availability) || availability.length === 0) {
      return { isAvailable: false, startPercent: 0, endPercent: 0 };
    }

    // Check each time range
    for (const [start, end] of availability) {
      const rangeStart = timeStringToMinutes(start);
      let rangeEnd = timeStringToMinutes(end);
      
      // Handle cases where the end time is "12:00 PM" (meaning end of day)
      if (end === "12:00 PM") {
        rangeEnd = 24 * 60; // End of day
      }

      // If this range overlaps with our hour
      if (rangeStart < hourEndMinutes && rangeEnd > hourStartMinutes) {
        // Calculate what percentage of the hour is available
        const startPercent = Math.max(0, Math.min(60, rangeStart - hourStartMinutes)) / 60 * 100;
        const endPercent = Math.max(0, Math.min(60, rangeEnd - hourStartMinutes)) / 60 * 100;
        
        return {
          isAvailable: true,
          startPercent,
          endPercent
        };
      }
    }

    return { isAvailable: false, startPercent: 0, endPercent: 0 };
  }

  // Calculate current time marker position
  function getCurrentTimePosition() {
    const now = new Date();
    const totalMinutes = now.getHours() * 60 + now.getMinutes();
    // Calculate position relative to the total width of the timeline
    // Each hour block is 101px wide, so multiply by the number of hours
    return (totalMinutes / (24 * 60)) * (101 * 24);
  }

  let timelineEl;

  onMount(() => {
    if (timelineEl) {
      // Set initial scroll position to show current time at 1/6 of the width
      const containerWidth = timelineEl.clientWidth;
      const currentHour = new Date().getHours();
      const scrollPosition = (currentHour * 100) - (containerWidth / 6);
      timelineEl.scrollLeft = Math.max(0, scrollPosition);
    }
  });

  // Format room ID to match photo filename pattern
  function getPhotoUrl(roomId, roomName) {
    if (!roomName) return null;

    const parts = roomName.replace("-", "").split(' ');
    if (parts.length < 2) return null;

    // const buildingMap = {
    //   'school of social work': 'school_of_social_work',
    //   'engineering terrace': 'engineering_terrace'
    // };

    let building = parts.slice(0, parts.length-1).join('_').toLowerCase();
    let roomNumber = parts[parts.length-1].toLowerCase();

    // if (building in buildingMap) {
    //   building = buildingMap[building];
    // }

    const photoPath = `/data/photos/${building}_${roomNumber}_1`;
    return `${photoPath}.jpg`;
  }
</script>

<div class="room">
  <div class="info-section">
    {#if getPhotoUrl(roomId, roomName)}
      <div class="photo-container">
        <img 
          src={getPhotoUrl(roomId, roomName)} 
          alt={roomName || `Room ${roomId}`}
          class="room-photo"
        />
      </div>
    {/if}
    <div class="room-details">
      <h2 class="room-name">{roomName || `Room ${roomId}`}</h2>
      <div class="badges">
        {#if roomInfo?.capacity}
          <span class="badge capacity">
            <i class="fas fa-users"></i> {roomInfo.capacity} seats
          </span>
        {/if}
        {#if roomInfo?.room_type}
          <span class="badge room-type">
            <i class="fas fa-door-open"></i> {roomInfo.room_type}
          </span>
        {/if}
        {#if roomInfo?.table_style}
          <span class="badge table-style">
            <i class="fas fa-table"></i> {roomInfo.table_style}
          </span>
        {/if}
        {#if roomInfo?.shared_tables}
          <span class="badge shared-tables">
            <i class="fas fa-chair"></i> {roomInfo.shared_tables} shared tables
          </span>
        {/if}
        {#if roomInfo?.board_type}
          <span class="badge board-type">
            <i class="fas fa-chalkboard"></i> {roomInfo.board_type}
          </span>
        {/if}
      </div>
    </div>
  </div>
  <div class="timeline-container">
    <div class="timeline" bind:this={timelineEl}>
      <div class="hours-container">
        {#each hours as hour}
          {@const availability = getHourAvailability(hour)}
          <div 
            class="hour"
            style="background: linear-gradient(to right, 
              #f0f0f0 0%, 
              #f0f0f0 {availability.startPercent}%, 
              #a7d7c9 {availability.startPercent}%, 
              #a7d7c9 {availability.endPercent}%, 
              #f0f0f0 {availability.endPercent}%
            )"
          >
            <div class="hour-label">{formatTime(hour)}</div>
          </div>
        {/each}
      </div>
      {#if typeof window !== 'undefined'}
        <div 
          class="current-time-marker" 
          style="left: {getCurrentTimePosition()}px"
        />
      {/if}
    </div>
  </div>
</div>

<style>
  .room {
    display: flex;
    margin: 1rem 0;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    overflow: hidden;
    height: 350px;
  }

  .info-section {
    width: 400px;
    min-width: 400px;
    height:100%;
    min-height: 350px;

    display: flex;
    flex-direction: column;
    border-right: 1px solid #eee;
  }

  .photo-container {
    height: 65%;
    overflow: hidden;
    border-bottom: 1px solid #eee;
  }

  .room-photo {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .room-details {
    padding: 1rem;
    height: 35%;
    overflow-y: auto;
  }

  .room-name {
    margin: 0 0 1rem 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #1a1a1a;
  }

  .badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .badge {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .badge i {
    font-size: 0.9rem;
  }

  .capacity { background: #e3f2fd; color: #1565c0; }
  .room-type { background: #f3e5f5; color: #7b1fa2; }
  .table-style { background: #e8f5e9; color: #2e7d32; }
  .shared-tables { background: #fff3e0; color: #ef6c00; }
  .board-type { background: #fce4ec; color: #c2185b; }

  .timeline-container {
    flex-grow: 1;
    overflow: hidden;
  }

  .timeline {
    position: relative;
    overflow-x: auto;
    height: 100%;
    scroll-behavior: smooth;
  }

  .hours-container {
    display: flex;
    height: 100%;
    width: fit-content;
    position: relative;
  }

  .hour {
    width: 100px;
    height: 100%;
    border-left: 1px solid #eee;
    position: relative;
    flex-shrink: 0;
  }

  .hour-label {
    position: absolute;
    top: 0.5rem;
    left: 0.5rem;
    font-size: 0.8rem;
    color: #666;
  }

  .current-time-marker {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #ff6b6b;
    z-index: 2;
    pointer-events: none;
  }
</style>