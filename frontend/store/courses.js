export const state = () => ({
    // The courses object
    courses: [],
  })
  
  export const actions = {
    async fetchCourses({ commit }) {
      const courses = await this.$axios.$get('/api/cursos/allCursos')
  
      commit('SET_COURSES', courses)
    },
  }
  
  export const getters = {
    getCourses: (state) => {
      return {
        courses: state.courses,
      }
    },
  }

  // to handle mutations
  export const mutations = {
    SET_COURSES(state, courses) {
      state.courses = courses
    },
  }