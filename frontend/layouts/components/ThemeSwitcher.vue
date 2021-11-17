<template>
  <v-fade-transition mode="out-in">
    <v-icon
      :key="$vuetify.theme.dark"
      @click="$vuetify.theme.dark = !$vuetify.theme.dark"
    >
      {{ $vuetify.theme.dark ? 'fas fa-lightbulb' : 'fa-moon' }}
    </v-icon>
  </v-fade-transition>
</template>

<script>
export default {}
</script>

<style></style>
