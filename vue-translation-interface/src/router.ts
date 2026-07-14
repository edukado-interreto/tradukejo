import { createRouter, createWebHistory } from "vue-router"
import { vueTranslationInterface } from "@/composables/useGlobals.ts"

import TranslateLanguage from "@/pages/TranslateLanguage.vue"

const LanguageChoice = () => import("@/pages/LanguageChoice.vue")

const baseURL = vueTranslationInterface.baseURL

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
    redirect: { name: "languageChoice" },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
