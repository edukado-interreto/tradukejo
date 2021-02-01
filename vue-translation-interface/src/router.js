import { createWebHistory, createRouter } from "vue-router";

import TranslateLanguage from './pages/TranslateLanguage';

const LanguageChoice = () => import('./pages/LanguageChoice');

const baseURL = window.vueTranslationInterface.baseURL;

const routes = [
  {
    path: baseURL,
    name: "languageChoice",
    component: LanguageChoice,
  },
  {
    path: baseURL + ":lang([a-z]{2,3})",
    name: "translateLanguage",
    component: TranslateLanguage,
  },
  {
    path: "/:catchAll(.*)",
    redirect: { name: "languageChoice" }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;