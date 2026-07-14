import axios from "axios"
import { createPinia } from "pinia"
import App from "@/App.vue"
import { vueTranslationInterface } from "@/composables/useGlobals.ts"
import i18n from "@/i18n.ts"
import router from "@/router.ts"

const pinia = createPinia()

const app = createApp(App)

app.use(i18n)
app.use(pinia)
app.use(router)

app.config.globalProperties.availableLanguages = vueTranslationInterface.availableLanguages
app.config.globalProperties.imgURL = vueTranslationInterface.imgURL
app.config.globalProperties.projectLanguage = vueTranslationInterface.projectLanguage
app.config.globalProperties.userId = vueTranslationInterface.userId
app.config.globalProperties.isAdmin = vueTranslationInterface.isAdmin
app.config.globalProperties.globals = vueTranslationInterface.globals

axios.defaults.baseURL = vueTranslationInterface.URLprefix
axios.defaults.headers.post["X-CSRFToken"] = app.config.globalProperties.csrf =
  vueTranslationInterface.csrf

app.mount("#app")
