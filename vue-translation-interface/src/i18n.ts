import { createI18n } from "vue-i18n"
import { vueTranslationInterface } from "@/composables/useGlobals.js"
import messages from "@/lang"

const currentLocale = vueTranslationInterface.currentLocale

type MessageSchema = (typeof messages)["eo"]

function pluralRuleFrench(choice: number) {
  return choice >= 2 ? 1 : 0
}

function pluralRulePolish(n: number) {
  return n === 1 ? 0 : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20) ? 1 : 2
}

function pluralRuleSlovak(n: number) {
  return n == 1 ? 0 : n >= 2 && n <= 4 ? 1 : 2
}

const i18n = createI18n<MessageSchema>({
  legacy: false,
  locale: currentLocale,
  fallbackLocale: "eo",
  messages,
  pluralizationRules: {
    fr: pluralRuleFrench,
    pl: pluralRulePolish,
    sk: pluralRuleSlovak,
    cs: pluralRuleSlovak,
  },
})

export default i18n
