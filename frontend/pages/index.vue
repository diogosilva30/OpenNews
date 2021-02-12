<template>
  <v-container fluid fill-height class="pa-0">
    <!-- Left side card -->
    <v-card tile flat class="d-flex diagonal" height="100%" width="70%">
      <v-row class="align-self-center" style="z-index: 5" no-gutters>
        <v-col cols="8" offset="2">
          <v-img
            src="/Logos/vector/default-monochrome.svg"
            alt="OpenNews logo"
            class="zoomOnHover"
          >
          </v-img>
        </v-col>
      </v-row>
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
        />
      </client-only>
    </v-card>

    <!-- Right side -->
    <v-card
      id="fadeBackground"
      class="d-inline-flex align-center flex-column"
      style="z-index: 0"
      height="100%"
      width="30%"
    >
      <!-- Place Social Media icons at most right and center screen -->
      <div
        class="ml-auto"
        style="
          position: fixed;
          top: 50%;
          right: 0;
          transform: translate(0, -50%);
        "
      >
        <!-- Social icons card -->
        <v-card
          v-for="icon in icons"
          :key="icon.id"
          outlined
          class="transparent"
        >
          <v-tooltip left>
            <template #activator="{ on, attrs }">
              <v-btn
                fab
                v-bind="attrs"
                class="transparent elevation-0"
                :href="icon.href"
                target="_blank"
                v-on="on"
              >
                <v-img :src="icon.src" max-width="30" contain></v-img>
              </v-btn>
            </template>
            <span>{{ icon.text }}</span>
          </v-tooltip>
        </v-card>
      </div>
      <!-- Place Get started button at bottom with flex auto margin -->
      <div class="mx-auto mb-10 mt-auto">
        <v-hover v-slot="{ hover }">
          <v-btn outlined x-large rounded :class="{ 'black--text': hover }"
            >Get started
          </v-btn>
        </v-hover>
      </div>
    </v-card>
  </v-container>
</template>

<script>
import Particles from '~/components/Particles.vue'

export default {
  components: { Particles },
  data: () => ({
    icons: [
      {
        src: '/SideMenu/GitHub-Mark-64px.png',
        href: 'https://github.com/spamz23/PT-NEWS_EXTRACTOR',
        text: 'GitHub',
      },
      {
        src: '/SideMenu/bmc-logo.svg',
        href: 'https://www.buymeacoffee.com/diogosilva',
        text: 'Buy me a coffee',
      },
    ],
  }),
}
</script>
<style scoped>
/* Diagonal cards */
.diagonal {
  position: relative;
  width: 120px;
  padding: 10px 20px 10px 10px;
  font-size: 20px;
  position: relative;
  color: #fff;
  background: #000000;
}
.diagonal::before {
  content: ' ';
  position: absolute;
  display: block;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 1;
  background: #000000;
  /* Transform */
  transform-origin: bottom left;
  -ms-transform: skew(-10deg, 0deg);
  -webkit-transform: skew(-10deg, 0deg);
  transform: skew(-10deg, 0deg);
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

/* Logo Zoom on hover */
.zoomOnHover {
  transition: transform 0.2s; /* Animation */
}
.zoomOnHover:hover {
  transform: scale(1.1);
}
</style>
