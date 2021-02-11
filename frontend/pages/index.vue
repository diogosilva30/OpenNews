<template>
  <v-container class="black" fluid fill-height>
    <v-row>
      <v-col cols="8" offset="2">
        <v-img src="/Logos/vector/default-monochrome.svg" alt="OpenNews logo">
        </v-img>
      </v-col>
      <v-col cols="2" class="d-flex justify-end align-center">
        <v-card class="purple lighten-4" rounded>
          <v-card-text>
            <v-img
              v-for="icon in icons"
              :key="icon.id"
              :src="icon"
              max-width="32"
              class="my-3"
            ></v-img>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data: () => ({
    icons: ['/SideMenu/GitHub-Mark-64px.png', '/SideMenu/bmc-logo.svg'],
  }),
}
</script>
