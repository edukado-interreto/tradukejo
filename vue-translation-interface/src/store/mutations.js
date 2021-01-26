const mutations = {
  setLanguage(state, payload) {
    state.currentLanguage = payload;
  },
  setStrings(state, payload) {
    state.loadedStrings = payload;
  },
  updateStringState(state, payload) {
    const index = state.loadedStrings.findIndex((element) => element.translated_text.id === payload.id);
    state.loadedStrings[index].state = payload.state;
  }
}

export default mutations