<template>
  <v-container id="fadeBackground" fluid fill-height>
    <v-row justify="center">
      <v-col md="6">
        <v-card class="black rounded-xl" rounded>
          <v-card-title class="justify-center">
            <div class="text-h2 mylight--text">Search News {{ step }}</div>
          </v-card-title>
          <v-card-text>
            <v-card class="mx-auto black" tile flat max-width="500">
              <v-card-title
                class="title font-weight-regular justify-space-between"
              >
                <span class="mylight--text">{{ currentTitle }}</span>
                <v-avatar
                  id="fadeBackground"
                  color="primary lighten-2"
                  class="subheading white--text"
                  size="24"
                  v-text="step"
                ></v-avatar>
              </v-card-title>

              <!-- Choose jornal -->
              <div v-if="step === 1">
                <v-card-text>
                  <v-select
                    v-model="selected_journal"
                    :items="supportedJournals"
                    outlined
                    prepend-icon="feed"
                    label="Journal"
                    color="myblue"
                    class="mypurple--text"
                    dark
                  >
                  </v-select>
                </v-card-text>
              </div>
              <!-- Choose type of search -->
              <div v-if="step === 2">
                <v-card-text>
                  <v-select
                    v-model="selected_search_type"
                    :items="supportedSearchTypes"
                    outlined
                    prepend-icon="feed"
                    label="Search type"
                    color="myblue"
                    class="mypurple--text"
                    dark
                  >
                  </v-select>
                </v-card-text>
              </div>

              <div v-if="step === 3">
                <v-card-text>
                  <v-select
                    v-model="selected_search_type"
                    :items="supportedSearchTypes"
                    outlined
                    prepend-icon="feed"
                    label="Search type"
                    color="myblue"
                    class="mypurple--text"
                    dark
                  >
                  </v-select>
                </v-card-text>
              </div>
              <v-card-actions>
                <v-btn
                  :disabled="step === 1"
                  color="mylight"
                  outlined
                  @click="setStep(step - 1)"
                >
                  Back
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  :disabled="step === 3"
                  color="mylight"
                  outlined
                  @click="setStep(step + 1)"
                >
                  Next
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data: () => ({
    supportedJournals: ['Público', 'Correio da Manhã'],
    selected_journal: null,
    selected_search_type: null,
  }),

  computed: {
    // eslint-disable-next-line vue/return-in-computed-property
    currentTitle() {
      switch (this.step) {
        case 1:
          return 'Select a journal.'
        case 2:
          return 'Select the type of search'
        case 3:
          return 'Account created'
      }
    },
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
    step() {
      // Get step from URL. Defaults to 1
      const urlStep = this.$route.query.step || 1
      // If step is greater than 4 , push to first step
      const parsedUrlStep = parseInt(urlStep)
      if (isNaN(parsedUrlStep) || parsedUrlStep >= 4) {
        this.setStep(1)
      }
      return parsedUrlStep
    },
    query() {
      return this.$route.query
    },
  },
  methods: {
    setStep(stepNumber) {
      this.$router.push({
        path: this.$route.path,
        query: { step: stepNumber },
      })
    },
  },
}
</script>
