<template>
  <div>
    <full-page>
      <section class="section">First section ...</section>
      <section class="section">Second section ...</section>
    </full-page>
  </div>
</template>
<script>
export default {}
</script>
<style scoped>
.zoom {
  transition: transform 0.2s; /* Animation */
}

.zoom:hover {
  transform: scale(
    1.5
  ); /* (150% zoom - Note: if the zoom is too large, it will go outside of the viewport) */
}
</style>
