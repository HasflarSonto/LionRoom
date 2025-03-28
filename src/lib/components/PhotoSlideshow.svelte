<script>
  export let photos = [];
  let currentIndex = 0;

  function nextPhoto() {
    currentIndex = (currentIndex + 1) % photos.length;
  }

  function previousPhoto() {
    currentIndex = (currentIndex - 1 + photos.length) % photos.length;
  }
</script>

<div class="relative h-96">
  {#if photos.length > 0}
    <img
      src={photos[currentIndex]}
      alt="Room photo"
      class="w-full h-full object-cover rounded-lg"
    />
    
    <!-- Navigation buttons -->
    <button
      class="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full"
      on:click={previousPhoto}
    >
      ←
    </button>
    <button
      class="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full"
      on:click={nextPhoto}
    >
      →
    </button>
    
    <!-- Photo counter -->
    <div class="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded">
      {currentIndex + 1} / {photos.length}
    </div>
  {/if}
</div> 