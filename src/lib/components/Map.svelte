<script>
  import { onMount } from 'svelte';
  export let location;
  
  let map;
  
  onMount(() => {
    // Initialize Google Maps
    map = new google.maps.Map(document.getElementById('map'), {
      center: { lat: location.lat, lng: location.lng },
      zoom: 17
    });
    
    // Add marker for the building
    new google.maps.Marker({
      position: { lat: location.lat, lng: location.lng },
      map: map,
      title: location.building
    });
  });
</script>

<div id="map" class="w-full h-96 rounded-lg"></div>

<svelte:head>
  <script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY"></script>
</svelte:head> 