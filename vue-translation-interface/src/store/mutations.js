const mutations = {
  setLanguage(state, payload) {
    state.currentLanguage = payload;
  },
  setStrings(state, payload) {
    state.loadedStrings = payload;
  },
  setDirectoriesTree(state, payload) {
    state.directoriesTree = payload;
  },
  setCanLoadMore(state, payload) {
    state.canLoadMore = payload;
  },
  addStrings(state, payload) {
    state.loadedStrings = state.loadedStrings.concat(payload);
  },
  updateStringState(state, payload) {
    const index = state.loadedStrings.findIndex((element) => element.translated_text.id === payload.id);
    state.loadedStrings[index].state = payload.state;
  },
  markDeleted(state, payload) {
    const index = state.loadedStrings.findIndex((element) => element.id === payload);
    state.loadedStrings[index].deleted = true;
  },
  undoDelete(state, payload) {
    const index = state.loadedStrings.findIndex((element) => element.id === payload);
    state.loadedStrings[index].deleted = false;
  },
  updateString(state, payload) {
    const index = state.loadedStrings.findIndex((element) => element.id === payload.id);
    state.loadedStrings[index] = payload;
  },
  addStringFirst(state, payload) {
    state.loadedStrings.unshift(payload);
  },
  setDirectoriesTreeLoading(state, payload) {
    state.directoriesTreeLoading = payload;
  }
}

export default mutations