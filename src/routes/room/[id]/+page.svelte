<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import PhotoSlideshow from '$lib/components/PhotoSlideshow.svelte';
  import RoomBadges from '$lib/components/RoomBadges.svelte';
  import Timeline from '$lib/components/Timeline.svelte';
  import Map from '$lib/components/Map.svelte';
  
  export let data;
  const roomId = $page.params.id;
  let roomInfo;
  let availability = [];

  onMount(async () => {
    try {
      // Fetch room info and availability in parallel
      const [infoRes, availRes] = await Promise.all([
        fetch(`/api/room-info/${roomId}`),
        fetch(`/api/room-availability/${roomId}`)
      ]);

      if (!infoRes.ok) throw new Error('Failed to fetch room info');
      if (!availRes.ok) throw new Error('Failed to fetch room availability');

      roomInfo = await infoRes.json();
      availability = await availRes.json();
    } catch (error) {
      console.error('Error loading room data:', error);
    }
  });
</script>

<div class="container mx-auto p-4">
  <!-- Top Row -->
  <div class="grid grid-cols-2 gap-4 mb-8">
    <!-- Left Column - Photo Slideshow -->
    <div class="bg-white rounded-lg shadow-lg p-4">
      {#if roomInfo?.photos}
        <PhotoSlideshow photos={roomInfo.photos} />
      {/if}
    </div>
    
    <!-- Right Column - Room Info and Button -->
    <div class="flex flex-col gap-4">
      <div class="bg-white rounded-lg shadow-lg p-4">
        {#if roomInfo}
          <RoomBadges {roomInfo} />
        {/if}
      </div>
      <div class="bg-white rounded-lg shadow-lg p-4">
        <a 
          href="https://ems.cuit.columbia.edu/EmsWebApp/BrowseForSpace.aspx" 
          target="_blank" 
          class="btn btn-primary w-full"
        >
          Book this room
        </a>
      </div>
    </div>
  </div>

  <!-- Middle Row - Timeline -->
  <div class="bg-white rounded-lg shadow-lg p-4 mb-8">
    {#if availability}
      <Timeline {availability} />
    {/if}
  </div>

  <!-- Bottom Row - Map -->
  <div class="bg-white rounded-lg shadow-lg p-4">
    {#if roomInfo?.location}
      <Map location={roomInfo.location} />
    {/if}
  </div>
</div> 