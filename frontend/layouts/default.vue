<template>
  <v-app>
    <v-main>
      <SocialMediaIcons />
      <nuxt />
    </v-main>
  </v-app>
</template>

<script>
import SocialMediaIcons from '~/components/SocialMediaIcons'

export default {
  components: {
    SocialMediaIcons,
  },
}
</script>
