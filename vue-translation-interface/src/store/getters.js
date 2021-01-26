const getters = {
  currentLanguage(state) {
    return {
      ...state.currentLanguage, // Make the object more like other object languages
      ...state.currentLanguage.fields,
      code: state.currentLanguage.pk,
    };
  },
  strings(state) {
    return state.loadedStrings;
  }
}

export default getters