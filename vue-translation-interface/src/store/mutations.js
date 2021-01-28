const mutations = {
  setLanguage(state, payload) {
    state.currentLanguage = payload;
  },
  setStrings(state, payload) {
    state.loadedStrings = payload;
  },
  setDirectories(state, payload) {
    state.loadedDirectories = payload;
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
  }
}

export default mutations