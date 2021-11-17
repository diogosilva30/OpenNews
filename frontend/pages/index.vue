<template>
  <v-container fill-height class="align-center justify-center">
    <v-row id="hero" no-gutters align="center" justify="center">
      <v-img
        :src="`/default-monochrome-text-${
          $vuetify.theme.dark ? 'white' : 'black'
        }.svg`"
      />
      <v-container>
        <v-row align="center" class="white--text mx-auto" justify="center">
          <v-col class="white--text text-center" cols="12" tag="h1">
            <span
              :class="[
                $vuetify.breakpoint.smAndDown ? 'display-1' : 'display-2'
              ]"
              class="font-weight-light"
            >
              WELCOME TO
            </span>

            <br />

            <span
              :class="[
                $vuetify.breakpoint.smAndDown ? 'display-3' : 'display-4'
              ]"
              class="font-weight-black"
            >
              VUETIFY
            </span>
          </v-col>

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
    </v-row>
    <v-row id="form">dqwd</v-row>
  </v-container>
</template>
<script>
export default {}
</script>
<style scoped>
.custom-loader {
  animation: loader 1s infinite;
  display: flex;
}

.zoom {
  transition: transform 0.2s; /* Animation */
}

.zoom:hover {
  transform: scale(
    1.5
  ); /* (150% zoom - Note: if the zoom is too large, it will go outside of the viewport) */
}
</style>
