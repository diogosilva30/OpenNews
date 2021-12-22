<template>
  <v-app :style="{ background: $vuetify.theme.themes[theme].background }">
    <v-app-bar app flat absolute color="transparent">
      <v-spacer />
      <theme-switcher></theme-switcher>
    </v-app-bar>

    <v-main>
      <nuxt-child />
    </v-main>

    <v-footer app inset color="transparent" absolute height="56" class="px-0">
      <div class="boxed-container w-full">
        <div class="mx-6 d-flex justify-space-between">
          <span> &copy; 2021 OpenNews </span>
        </div>
      </div>
    </v-footer>
  </v-app>
</template>

<script>
import ThemeSwitcher from './components/ThemeSwitcher.vue'
export default {
  components: {
    ThemeSwitcher
  },
  data() {
    return {
      drawer: false
    }
  },
  computed: {
    theme() {
      return this.$vuetify.theme.dark ? 'dark' : 'light'
    }
  }
}
</script>
<style lang="scss" scoped>
.boxed-container {
  max-width: 1440px;
  margin-left: auto;
  margin-right: auto;
}
.search {
  max-width: 350px;
  max-height: 32px;
}
</style>
