import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js';
import store from './store/index.js';
import i18n from './i18n.js';
import mixins from './mixins.js';
import axios from 'axios';
import mitt from 'mitt';

import LoadingSpinner from './components/ui/LoadingSpinner';

const app = createApp(App);
const eventBus = mitt()

app.use(router);
app.use(store);
app.use(i18n);
app.mixin(mixins);

app.config.globalProperties.availableLanguages = window.vueTranslationInterface.availableLanguages;
app.config.globalProperties.imgURL = window.vueTranslationInterface.imgURL;
app.config.globalProperties.projectLanguage = window.vueTranslationInterface.projectLanguage;
app.config.globalProperties.userId = window.vueTranslationInterface.userId;
app.config.globalProperties.isAdmin = window.vueTranslationInterface.isAdmin;
app.config.globalProperties.globals = window.vueTranslationInterface.globals;
app.config.globalProperties.eventBus = eventBus; // https://shouts.dev/data-pass-between-components-using-eventbus-in-vue3

axios.defaults.baseURL = window.vueTranslationInterface.URLprefix;
axios.defaults.headers.post['X-CSRFToken'] = app.config.globalProperties.csrf = window.vueTranslationInterface.csrf;

app.component('loading-spinner', LoadingSpinner);

app.mount('#app');