const getters = {
  currentLanguage(state) {
    return state.currentLanguage;
  },
  directories(state) {
    return state.loadedDirectories;
  },
  strings(state) {
    return state.loadedStrings;
  },
  indexOfString: (state) => (id) => {
    return state.loadedStrings.findIndex((element) => element.id === id);
  }
}

export default getters