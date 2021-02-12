<template>
  <v-app>
    <v-container fluid fill-height class="pa-0 mydark">
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
      <v-row align="center" justify="center">
        <v-col md="6">
          <v-card-title
            class="py-0 text-h1 justify-center mylight--text font-weight-black"
            >ARE YOU LOST?
          </v-card-title>
          <v-card-title
            class="mb-8 text-h3 justify-center mylight--text font-weight-bold"
          >
            ERROR 404
          </v-card-title>
          <v-card class="text-center transparent" style="z-index: 999">
            <v-btn outlined nuxt to="/" x-large rounded class="mylight--text"
              >Pull me back
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
h1 {
  font-size: 20px;
}
/* Particles */
#particles-instance- {
  height: 100vh !important;
  position: absolute;
  top: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: 1 !important;
}
</style>
