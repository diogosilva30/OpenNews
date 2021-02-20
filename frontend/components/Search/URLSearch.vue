<template>
  <div class="transparent">
    <v-card class="transparent">
      <p class="mr-3 text-right">
        <b>{{ urls.length }}</b> URLs
      </p>
      <v-card-text>
        <ValidationObserver ref="observer">
          <ValidationProvider
            v-slot="{ errors }"
            vid="url"
            name="Url"
            rules="url"
          >
            <v-text-field
              v-model="newURL"
              :error-messages="errors"
              name="newURL"
              label="Insert a News URL"
              @keydown.enter="addURL"
            />
          </ValidationProvider>
        </ValidationObserver>
        <template v-if="urls.length == 0">You have 0 URLs, add some</template>
        <template v-else>
          <v-data-table
            :headers="headers"
            :items="urls"
            :search="search"
            class="transparent"
          >
          </v-data-table>
        </template>
      </v-card-text>
    </v-card>
  </div>
</template>
<script>
import { mapGetters } from 'vuex'
import { ValidationProvider, ValidationObserver } from 'vee-validate'

export default {
  components: {
    ValidationProvider,
    ValidationObserver,
  },

  data() {
    return {
      newURL: null,
      headers: [
        {
          text: 'URL',
          align: 'center',
          value: 'url',
        },
      ],
      search: '',
    }
  },
  computed: {
    ...mapGetters('url_search', {
      // map `this.urls` to the store getter
      urls: 'getURLs',
    }),
  },
  methods: {
    addURL() {
      const value = this.newURL && this.newURL.trim()
      if (!value || this.urls.some((el) => el.url === value).length > 0) {
        return
      }
      // Commit URL to store
      this.$store.commit('url_search/add', value)
      // Clear URL
      this.newURL = null
    },
    removeURL(index) {
      this.urls.splice(index, 1)
    },
  },
}
</script>
