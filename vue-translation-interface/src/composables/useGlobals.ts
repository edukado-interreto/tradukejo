type VueTranslationInterface = {
  projectId: string
  csrf: string
  baseURL: string
  imgURL: string
  currentLocale: string
  URLprefix: string
  projectLanguage: string
  availableLanguages: Language[]
  userId: number
  isAdmin: boolean
  globals: {
    TRANSLATION_STATE_TRANSLATED: number
    TRANSLATION_STATE_UNTRANSLATED: number
    TRANSLATION_STATE_OUTDATED: number
    STATE_FILTER_ALL: string
    STATE_FILTER_UNTRANSLATED: string
    STATE_FILTER_OUTDATED: string
    STATE_FILTER_OUTDATED_UNTRANSLATED: string
    SORT_STRINGS_BY_NEWEST: string
    SORT_STRINGS_BY_OLDEST: string
    SORT_STRINGS_BY_NAME: string
  }
}

export const vueTranslationInterface: VueTranslationInterface = JSON.parse(
  document.getElementById("vueTranslationInterface")?.textContent || "{}",
)

export function useGlobals() {
  return { vueTranslationInterface, globals: vueTranslationInterface.globals }
}
