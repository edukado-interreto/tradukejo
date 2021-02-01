const getters = {
  currentLanguage(state) {
    return state.currentLanguage || null;
  },
  directories(state) {
    return state.loadedDirectories;
  },
  strings(state) {
    return state.loadedStrings;
  },
  canLoadMore(state) {
    return state.canLoadMore;
  },
  indexOfString: (state) => (id) => {
    return state.loadedStrings.findIndex((element) => element.id === id);
  },
  allStringIds(state) {
    const ids = [];
    state.loadedStrings.forEach((s) => ids.push(s.id));
    return ids;
  }
}

export default getters