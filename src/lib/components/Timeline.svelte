<script>
  export let availability = [];
  
  const hours = Array.from({ length: 24 }, (_, i) => i);
  
  function isTimeAvailable(hour) {
    // Convert hour to minutes since midnight
    const minutes = hour * 60;
    return availability.some(([start, end]) => {
      const startMinutes = parseInt(start);
      const endMinutes = parseInt(end);
      return minutes >= startMinutes && minutes < endMinutes;
    });
  }
</script>

<div class="overflow-x-auto">
  <div class="flex min-w-max">
    {#each hours as hour}
      <div 
        class="w-16 h-16 border-r border-gray-200 relative {isTimeAvailable(hour) ? 'bg-green-100' : 'bg-gray-50'}"
      >
        <div class="absolute top-0 left-0 text-xs p-1">
          {hour === 0 ? '12 AM' : 
           hour === 12 ? '12 PM' : 
           hour > 12 ? `${hour-12} PM` : 
           `${hour} AM`}
        </div>
      </div>
    {/each}
  </div>
</div> 