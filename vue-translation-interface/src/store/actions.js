import axios from "axios";

const availableLanguages = window.vueTranslationInterface.availableLanguages;

async function postCsrf(url, data) {
  console.log(data);
  return await axios.post(url, data, { headers: { 'X-CSRFToken': window.vueTranslationInterface.csrf } });
}

const actions = {
  setLanguage(context, payload) {
    const language = availableLanguages.find(element => element.pk === payload);
    context.commit('setLanguage', language);
  },
  async fetchStrings(context, payload) {
    await postCsrf('/vue/get-strings/', {
      project_id: window.vueTranslationInterface.projectId,
      language: context.getters.currentLanguage.code,
      dir: payload.currentDirectory,
      q: payload.searchString,
      state: payload.stateFilter,
      sort: payload.sort,
    })
      .then((response) => {
        context.commit('setStrings', response.data.strings);
      })
      .catch(function (error) {
        console.log(error);
      });
  },
  async updateStringState(context, payload) {
    const url = payload.translated ? '/vue/mark-translated/' : '/vue/mark-outdated/';
    await postCsrf(url, {
      trstringtext_id: payload.id,
    })
      .then((response) => {
        context.commit('updateStringState', { id: payload.id, state: response.data.state})
      })
      .catch(function (error) {
        console.log(error);
      });
  }
}

export default actions