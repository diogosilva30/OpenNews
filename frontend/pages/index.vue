<template>
  <full-page>
    <section class="section">
      <v-container fill-height class="align-center justify-center">
        <v-row id="hero" no-gutters align="center" justify="center">
          <v-col lg="8">
            <v-img
              :src="`/default-monochrome-text-${
                $vuetify.theme.dark ? 'white' : 'black'
              }.svg`"
            />
          </v-col>
        </v-row>
        <v-row align="center" class="white--text mx-auto" justify="center">
          <v-btn
            class="align-self-end zoom"
            color="button"
            icon
            x-large
            expand-on-hover
            @click="$vuetify.goTo('#form')"
          >
            <v-icon>fa-arrow-alt-circle-down</v-icon>
          </v-btn>
        </v-row>
      </v-container>
      <section class="section">First section ...</section>
    </section>
  </full-page>
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
