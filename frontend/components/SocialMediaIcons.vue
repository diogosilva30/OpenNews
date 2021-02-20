<template>
  <!-- Place Social Media icons at most right and center screen, above everything-->
  <div
    class="ml-auto"
    style="
      position: fixed;
      top: 50%;
      right: 0;
      transform: translate(0, -50%);
      z-index: 1000;
    "
  >
    <!-- Social icons card -->
    <v-card v-for="icon in icons" :key="icon.id" outlined class="transparent">
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
        href: 'https://www.buymeacoffee.com/diogosilva',
        text: 'Buy me a coffee',
      },
    ],
  }),
}
</script>
