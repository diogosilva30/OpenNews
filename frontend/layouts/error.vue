<template>
  <v-app>
    <v-container fluid fill-height class="mydark">
      <!-- Particle background effects -->
      <client-only>
        <Particles
          color="#DCBA8F"
          :particles-number="150"
          shape-type="circle"
          :particle-size="2"
          movement-direction="right"
          lines-color="#dedede"
          :line-linked="true"
          :move-speed="0.75"
          :hover-effect="true"
      /></client-only>
      <!-- Make sure content is above background (z-index = 2) -->
      <v-row align="center" justify="center" style="z-index: 2">
        <v-col md="8">
          <v-card-text
            class="py-0 text-h1 mylight--text font-weight-black text-center"
            style="word-break: normal"
          >
            <template v-if="error.statusCode === 404">
              <span>ARE YOU LOST? </span>
            </template>
            <template v-else>AN ERROR OCCURED</template>
          </v-card-text>
          <v-card-title
            class="mb-8 text-h3 justify-center mylight--text font-weight-bold"
          >
            <template v-if="error.statusCode === 404"> ERROR 404 </template>
            <template v-else>ERROR 500</template>
          </v-card-title>
          <v-card class="text-center transparent">
            <v-btn outlined nuxt to="/" x-large rounded class="mylight--text">
              Pull me back
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
export default {
  layout: 'empty',
  props: {
    error: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      pageNotFound: '404 Not Found',
      otherError: 'An error occurred',
    }
  },
  head() {
    const title =
      this.error.statusCode === 404 ? this.pageNotFound : this.otherError
    return {
      title,
    }
  },
}
</script>

<style scoped>
/* Particles */
#particles-instance- {
  height: 100vh !important;
  position: absolute;
  top: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  left: 0 !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: 1 !important;
}
</style>
