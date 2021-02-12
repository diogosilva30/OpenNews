<template>
  <v-container id="fadeBackground" fluid fill-height>
    <v-row justify="center">
      <v-col md="6">
        <v-card class="black rounded-xl" rounded>
          <v-card-title class="justify-center">
            <div class="text-h2 mylight--text">Search News</div>
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
              <v-window v-model="step">
                <v-window-item :value="1">
                  <v-card-text>
                    <v-select
                      :items="supportedJournals"
                      outlined
                      prepend-icon="feed"
                      label="Journal"
                      color="myblue"
                    >
                    </v-select>
                  </v-card-text>
                </v-window-item>

                <v-window-item :value="2">
                  <v-card-text>
                    <v-text-field
                      label="Password"
                      type="password"
                    ></v-text-field>
                    <v-text-field
                      label="Confirm Password"
                      type="password"
                    ></v-text-field>
                    <span class="caption grey--text text--darken-1">
                      Please enter a password for your account
                    </span>
                  </v-card-text>
                </v-window-item>

                <v-window-item :value="3">
                  <div class="pa-4 text-center">
                    <v-img
                      class="mb-4"
                      contain
                      height="128"
                      src="https://cdn.vuetifyjs.com/images/logos/v.svg"
                    ></v-img>
                    <h3 class="title font-weight-light mb-2">
                      Welcome to Vuetify
                    </h3>
                    <span class="caption grey--text"
                      >Thanks for signing up!</span
                    >
                  </div>
                </v-window-item>
              </v-window>

              <v-card-actions>
                <v-btn :disabled="step === 1" text @click="step--">
                  Back
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  :disabled="step === 3"
                  color="white"
                  outlined
                  @click="step++"
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
    step: 1,
    supportedJournals: ['Público', 'Correio da Manhã'],
  }),

  computed: {
    currentTitle() {
      switch (this.step) {
        case 1:
          return 'Select a journal.'
        case 2:
          return 'Create a password'
        default:
          return 'Account created'
      }
    },
  },
}
</script>
