<template>
  <v-container fluid style="height: 100vh" class="fadeBackground">
    <!-- Take 8 columns on medium or larger displays -->
    <v-row justify="center" class="ma-4" no-gutters>
      <v-col md="8" cols="12">
        <v-app-bar color="mydark">
          <!-- Particle background effects -->
          <client-only>
            <Particles
              class="pa-0 ma-0"
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
          <!-- Wrap title into v-spacers to justify center -->
          <v-spacer></v-spacer>
          <v-toolbar-title class="text-h2 mylight--text pa-3">
            {{ title }}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <!-- Tabs -->
          <template #extension>
            <v-tabs
              v-model="step"
              background-color="transparent"
              color="myblue"
              grow
              dark
            >
              <!-- Disable every tab, except the current one -->
              <v-tab
                v-for="item in items"
                :key="item.step"
                :disabled="item.step != step"
              >
                {{ item.text }}
              </v-tab>
            </v-tabs>
          </template>
        </v-app-bar>
      </v-col>
    </v-row>
    <v-row justify="center" class="ma-4" no-gutters>
      <v-col md="8" cols="12">
        <v-card class="transparent" rounded>
          <v-card-text class="mx-auto">
            <v-card class="mx-auto transparent" tile flat max-width="500">
              <v-tabs-items v-model="step" class="transparent">
                <v-tab-item v-for="item in items" :key="item.id">
                  <!-- If first step display Journal selection -->
                  <template v-if="item.step === 0">
                    <v-select
                      v-model="selected_journal"
                      :items="supportedJournals"
                      outlined
                      prepend-icon="feed"
                      label="Journal"
                      color="myblue"
                      class="mypurple--text pa-2"
                      dark
                    >
                    </v-select>
                  </template>
                  <!-- If second step display search type selection -->
                  <template v-if="item.step === 1">
                    <v-select
                      v-model="selected_search_type"
                      :items="supportedSearchTypes"
                      outlined
                      prepend-icon="search"
                      label="Search type"
                      color="myblue"
                      class="mypurple--text pa-2"
                      dark
                    >
                    </v-select>
                  </template>
                  <!-- If third step display dynamic detail filling component -->
                  <template v-if="item.step === 2">
                    <component :is="componentName"></component>
                  </template>
                </v-tab-item>
              </v-tabs-items>

              <v-card-actions>
                <v-btn
                  :disabled="step === 0"
                  color="mylight"
                  outlined
                  @click="setStep(step - 1)"
                >
                  Back
                </v-btn>
                <v-spacer></v-spacer>

                <!-- Do not display next button on last step -->
                <template v-if="step !== 2">
                  <v-btn color="mylight" outlined @click="setStep(step + 1)">
                    Next
                  </v-btn>
                </template>
                <!-- Instead display a 'Search' button -->
                <!-- to submit the search to the API -->
                <template v-if="step === 2">
                  <v-btn
                    color="mylight"
                    outlined
                    :disabled="!isSearchValid"
                    @click="search()"
                  >
                    Submit
                  </v-btn>
                </template>
              </v-card-actions>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Particles from '~/components/Particles.vue'

export default {
  components: { Particles },
  data: () => ({
    supportedJournals: ['Público', 'Correio da Manhã'],
    selected_journal: null,
    selected_search_type: null,
    title: 'News Search',
    items: [
      { text: 'Select Journal', step: 0 },
      { text: 'Select Search Type', step: 1 },
      { text: 'Fill Search Details', step: 2 },
    ],
    step: 0,
  }),
  head() {
    return {
      title: this.title,
    }
  },
  computed: {
    supportedSearchTypes() {
      switch (this.selected_journal) {
        case 'Público':
          return ['URL Search', 'Tag Search', 'Keywords Search']
        case 'Correio da Manhã':
          return ['URL Search', 'Tag Search']
        default:
          return []
      }
    },
    componentName() {
      // The dynamic component is choosen depending on
      // the selected search type
      switch (this.selected_search_type) {
        case 'URL Search':
          return 'URLSearch'
        case 'TagSearch':
          return 'TagSearch'
        case 'Keywords Search':
          return 'KeywordsSearch'
        default:
          return ''
      }
    },
    // Checks is the currently selected search is valid
    isSearchValid() {
      switch (this.selected_search_type) {
        case 'URL Search':
          return this.$store.getters['url_search/isValid']
        case 'TagSearch':
          return this.$store.getters['tag_search/isValid']
        case 'Keywords Search':
          return this.$store.getters['keywords_search/isValid']
        default:
          return ''
      }
    },
  },
  methods: {
    setStep(value) {
      this.step = value
    },
  },
}
</script>
<style scoped>
/* Particles */
#particles-instance- {
  position: absolute;
  top: 0 !important;
  margin: 0 !important;
  left: 0 !important;
  padding: 0 !important;
  width: 100% !important;
  height: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
  z-index: -1 !important;
}
</style>
