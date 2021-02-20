export const state = () => ({
  urls: [],
})

export const mutations = {
  // Mutation to add 1 URL to list
  add(state, url) {
    state.urls.push({
      url,
    })
  },
  // Mutation to remove 1 URL from list
  remove(state, { url }) {
    state.list.splice(state.list.indexOf(url), 1)
  },
}

export const getters = {
  // Returns if the state is valid (At least 1 URL)
  isValid: (state) => {
    return state.urls.length >= 1
  },
  // Returns the list of URLs
  getURLs: (state) => {
    return state.urls
  },
}
