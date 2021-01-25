import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js';
import store from './store/index.js';


const app = createApp(App);

app.use(router);
app.use(store);

app.config.globalProperties.availableLanguages = window.vueTranslationInterface.availableLanguages;
app.config.globalProperties.projectId = window.vueTranslationInterface.projectId;
app.config.globalProperties.globals = window.vueTranslationInterface.globals;

app.mount('#app');