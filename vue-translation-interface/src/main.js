import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js';
import store from './store/index.js';
import mixins from './mixins.js';

import LoadingSpinner from './components/ui/LoadingSpinner';

const app = createApp(App);

app.use(router);
app.use(store);
app.mixin(mixins);

app.config.globalProperties.availableLanguages = window.vueTranslationInterface.availableLanguages;
app.config.globalProperties.csrf = window.vueTranslationInterface.csrf;
app.config.globalProperties.imgURL = window.vueTranslationInterface.imgURL;
app.config.globalProperties.projectLanguage = window.vueTranslationInterface.projectLanguage;
app.config.globalProperties.userId = window.vueTranslationInterface.userId;
app.config.globalProperties.isAdmin = window.vueTranslationInterface.isAdmin;
app.config.globalProperties.globals = window.vueTranslationInterface.globals;

app.component('loading-spinner', LoadingSpinner);

app.mount('#app');