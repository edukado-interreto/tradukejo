import { createStore } from 'vuex';

const availableLanguages = window.vueTranslationInterface.availableLanguages;

const store = createStore({
  state() {
    return {
      currentLanguage: null,
    };
  },
  getters: {
    currentLanguage(state) {
      return state.currentLanguage;
    },
  },
  mutations: {
    setLanguage(state, payload) {
      state.currentLanguage = payload;
    }
  },
  actions: {
    setLanguage(context, payload) {
      const language = availableLanguages.find(element => element.pk === payload);
      context.commit('setLanguage', language);
    }
  },
});

export default store;