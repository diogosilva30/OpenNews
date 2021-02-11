<template>
  <v-container fluid fill-height class="pa-0">
    <!-- Left side card -->
    <v-card tile flat class="d-flex diagonal" height="100%" width="70%">
      <v-row class="align-self-center" style="z-index: 5" no-gutters>
        <v-col cols="8" offset="2">
          <v-img
            class="logo"
            src="/Logos/vector/default-monochrome.svg"
            alt="OpenNews logo"
          >
          </v-img>
        </v-col>
      </v-row>
    </v-card>
    <!-- Right side card -->
    <v-card
      tile
      flat
      class="d-flex"
      style="z-index: 0"
      height="100%"
      width="30%"
    >
      <v-img id="fadeBackground" class="d-flex align-center">
        <!-- SOCIAL ICONS -->
        <!-- justify-end to align items to the right -->
        <v-row class="justify-end" height no-gutters>
          <v-card class="transparent" flat>
            <v-row v-for="icon in icons" :key="icon.id" class="ma-3">
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
            </v-row>
          </v-card>
        </v-row>
      </v-img>
    </v-card>
  </v-container>
</template>

<script>
export default {
  data: () => ({
    icons: [
      {
        src: '/SideMenu/GitHub-Mark-64px.png',
        href: 'https://github.com/spamz23/PT-NEWS_EXTRACTOR',
        text: 'GitHub',
      },
      {
        src: '/SideMenu/bmc-logo.svg',
        href: 'https://github.com/spamz23/PT-NEWS_EXTRACTOR',
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
/* Animated gradient background */
#fadeBackground {
  background: linear-gradient(10deg, #b43eff, #c574f7, #23a6d5, #0a7196);
  background-size: 400% 400%;
  animation: gradient 10s ease-in-out infinite;
}

@keyframes gradient {
  0% {
    background-position: 0 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0 50%;
  }
}
</style>
