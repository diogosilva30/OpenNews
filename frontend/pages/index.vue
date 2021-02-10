<template>
  <v-container fluid fill-height class="blue">
    <v-row>
      <v-card tile flat class="white" width="70%" height="100vh"></v-card>
      <v-card id="test" tile flat class="white" width="20%" height="100vh">
      </v-card>
    </v-row>
  </v-container>
</template>

<script>
export default {}
</script>
<style scoped>
#test {
  -webkit-transform: skewX(-5deg);
  -moz-transform: skewX(-5deg);
  -ms-transform: skewX(-5deg);
  -o-transform: skewX(-5deg);
  transform: skewX(-5deg);
}
</style>
