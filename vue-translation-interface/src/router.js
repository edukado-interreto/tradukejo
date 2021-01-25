import { createWebHistory, createRouter } from "vue-router";

import LanguageChoice from './pages/LanguageChoice';
import TranslateLanguage from './pages/TranslateLanguage';

const baseURL = window.vueTranslationInterface.baseURL;

const routes = [
    {
        path: baseURL,
        name: "languageChoice",
        component: LanguageChoice,
    },
    {
        path: baseURL + ":lang",
        name: "translateLanguage",
        component: TranslateLanguage,
    },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;