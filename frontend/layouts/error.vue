<template>
  <v-app>
    <v-container fluid fill-height class="pa-0">
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
          <v-card-title class="justify-center">404 </v-card-title>
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
