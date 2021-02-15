import axios from "axios";

const availableLanguages = window.vueTranslationInterface.availableLanguages;

async function postCsrf(url, data) {
  return await axios.post(url, data, { headers: { 'X-CSRFToken': window.vueTranslationInterface.csrf } });
}

const actions = {
  setLanguage(context, payload) {
    const language = availableLanguages.find(element => element.code === payload);
    context.commit('setLanguage', language);
  },
  async fetchStrings(context, payload) {
    await postCsrf('/vue/get-strings/', {
      project_id: window.vueTranslationInterface.projectId,
      language: context.getters.currentLanguage.code,
      dir: payload.dir,
      q: payload.q,
      state: payload.state,
      sort: payload.sort,
      chosen_string: payload.chosen_string,
    })
      .then((response) => {
        context.commit('setStrings', response.data.strings);
        context.commit('setCanLoadMore', response.data.can_load_more);
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
  },
  async fetchDirectoriesTree(context, payload) {
    await postCsrf('/vue/get-directories-tree/', {
      project_id: window.vueTranslationInterface.projectId,
      language: context.getters.currentLanguage.code,
      q: payload.q,
      state: payload.state,
    })
      .then((response) => {
        context.commit('setDirectoriesTree', response.data.directories_tree);
      })
      .catch(function (error) {
        console.log(error);
      });
  },
  async deleteString(context, payload) {
    context.commit('markDeleted', payload);
    await postCsrf('/vue/delete-string/', {
      trstring_id: payload,
    })
      .catch(function (error) {
        console.log(error);
        context.commit('undoDelete', payload);
      });
  },
  async saveTranslation(context, payload) {
    await postCsrf('/vue/save-translation/', {
      language: context.getters.currentLanguage.code,
      ...payload
    })
      .then((response) => {
        context.commit('updateString', response.data);
      })
      .catch(function (error) {
        throw new Error(error.response.data);
      });
  },
  async addString(context, payload) {
    let data = null;
    await postCsrf('/vue/add-string/', {
      project_id: window.vueTranslationInterface.projectId,
      ...payload
    })
      .then((response) => {
        context.commit('addStringFirst', response.data);
        data = response.data;
      })
      .catch(function (error) {
        throw new Error(error.response.data);
      });
    return data;
  },
  async loadMore(context, payload) {
    await postCsrf('/vue/get-strings/', {
      project_id: window.vueTranslationInterface.projectId,
      language: context.getters.currentLanguage.code,
      dir: payload.dir,
      q: payload.q,
      state: payload.state,
      sort: payload.sort,
      previous_ids: context.getters.allStringIds
    })
      .then((response) => {
        context.commit('addStrings', response.data.strings);
        context.commit('setCanLoadMore', response.data.can_load_more);
      })
      .catch(function (error) {
        console.log(error);
      });
  },
}

export default actions