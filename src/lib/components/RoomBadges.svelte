<script>
  export let roomInfo;

  const badges = [
    { key: 'capacity', label: 'Capacity', icon: '👥' },
    { key: 'room_type', label: 'Room Type', icon: '🏢' },
    { key: 'seating_style', label: 'Seating', icon: '💺' },
    { key: 'table_style', label: 'Tables', icon: '🪑' },
    { key: 'board_type', label: 'Board', icon: '📝' },
    { key: 'has_projector', label: 'Projector', icon: '📽️' }
  ];
</script>

<div class="grid grid-cols-2 gap-4">
  {#each badges as badge}
    {#if roomInfo[badge.key] !== null}
      <div class="flex items-center gap-2 bg-gray-100 p-3 rounded-lg">
        <span class="text-xl">{badge.icon}</span>
        <div>
          <div class="text-sm text-gray-500">{badge.label}</div>
          <div class="font-semibold">
            {#if typeof roomInfo[badge.key] === 'boolean'}
              {roomInfo[badge.key] ? 'Yes' : 'No'}
            {:else}
              {roomInfo[badge.key]}
            {/if}
          </div>
        </div>
      </div>
    {/if}
  {/each}
</div> 