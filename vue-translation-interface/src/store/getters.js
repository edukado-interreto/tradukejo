const getters = {
  currentLanguage(state) {
    return state.currentLanguage || null;
  },
  directoriesTree(state) {
    return state.directoriesTree;
  },
  directoriesTreeLoading(state) {
    return state.directoriesTreeLoading;
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