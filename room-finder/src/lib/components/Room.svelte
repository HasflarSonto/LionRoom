<script>
  import { onMount } from 'svelte';
  export let roomId;
  export let availability;
  export let roomName;

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

  let currentTimePosition = 0;
  let timelineEl;

  function scrollToCurrentTime() {
    if (!timelineEl) return;
    
    // Get the current scroll container width
    const containerWidth = timelineEl.clientWidth;
    
    // Calculate scroll position to put current time marker 1/3 from the left
    const scrollPosition = currentTimePosition - (containerWidth / 3);
    
    // Scroll to position
    timelineEl.scrollLeft = Math.max(0, scrollPosition);
  }

  onMount(() => {
    // Update current time position every minute
    const updatePosition = () => {
      currentTimePosition = getCurrentTimePosition();
    };
    
    // Set initial position
    updatePosition();
    
    // Scroll to current time after a short delay to ensure DOM is ready
    setTimeout(scrollToCurrentTime, 100);
    
    // Update every minute
    const interval = setInterval(() => {
      updatePosition();
    }, 60000);
    
    // Cleanup interval on component destroy
    return () => clearInterval(interval);
  });
</script>

<div class="room">
  <div class="room-info">
    <div class="room-name">{roomName || `Room ${roomId}`}</div>
  </div>
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
        style="left: {currentTimePosition}px"
      />
    {/if}
  </div>
</div>

<style>
  .room {
    display: flex;
    margin: 1rem 0;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    overflow: hidden;
  }

  .room-info {
    width: 200px;
    min-width: 200px;
    padding: 1rem;
    background: #f8f9fa;
    border-right: 1px solid #ddd;
    flex-shrink: 0;
    display: flex;
    align-items: center;
  }

  .room-name {
    margin: 0;
    font-size: 1rem;
    font-weight: 500;
    word-wrap: break-word;
    word-break: break-word;
    hyphens: auto;
  }

  .timeline {
    position: relative;
    flex-grow: 1;
    overflow-x: auto;
    scroll-behavior: smooth;
  }

  .hours-container {
    display: flex;
    min-width: max-content;
    height: 100%;
  }

  .hour {
    width: 100px;
    height: 100%;
    border-left: 1px solid #e5e5e5;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    background: #f0f0f0;
  }

  .hour-label {
    font-size: 0.8rem;
    color: #333;
    position: absolute;
    top: 5px;
    left: 5px;
    font-weight: 400;
  }

  .current-time-marker {
    position: absolute;
    top: 0;
    width: 2px;
    height: 100%;
    background: #ff6b6b;
    z-index: 2;
  }
</style>