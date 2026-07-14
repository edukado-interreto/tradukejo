import type { AxiosError } from "axios"
import axios from "axios"
import { defineStore } from "pinia"
import { vueTranslationInterface } from "@/composables/useGlobals.ts"

const { availableLanguages } = vueTranslationInterface
const projectId = vueTranslationInterface.projectId

type StateResult = {
  state: number
}

type StringsResult = {
  strings: TrString[]
  can_load_more: boolean
}

type DirectoryTreeResult = {
  directories_tree: DirectoryTree
}

const log_missing_language = () => {
  console.error("src/store.ts: Language not defined before fetching data")
}

export const useStore = defineStore("", () => {
  const currentLanguage: Ref<Language | null> = ref(null)
  const strings: Ref<TrString[]> = ref([])
  const directoriesTree: Ref<DirectoryTree> = ref({})
  const canLoadMore = ref(false)
  const directoriesTreeLoading = ref(false)

  const indexOfString = computed(() => {
    return (id: number) => strings.value.findIndex((element) => element.id === id)
  })

  const allStringIds = computed(() => {
    return strings.value.map((s) => s.id)
  })

  function setLanguage(code: LanguageCode) {
    const language = availableLanguages.find((el: Language) => el.code === code)
    currentLanguage.value = language || null
  }

  async function fetchStrings(query: FetchStringsPayload) {
    if (currentLanguage.value === null) return log_missing_language()
    const language = currentLanguage.value.code
    const payload = { project_id: projectId, language, ...query }
    try {
      const response = await axios.post<StringsResult>("/vue/get-strings/", payload)
      strings.value = response.data.strings
      canLoadMore.value = response.data.can_load_more
    } catch (error) {
      console.error(error)
    }
  }

  async function updateStringState(text: UpdateStringStatePayload) {
    const url = text.translated ? "/vue/mark-translated/" : "/vue/mark-outdated/"
    const trstring = strings.value.find(
      (el) => el.translated_text && el.translated_text.id === text.id,
    )
    try {
      const response = await axios.post<StateResult>(url, { trstringtext_id: text.id })
      if (trstring) trstring.state = response.data.state
    } catch (error) {
      console.error(error)
    }
  }

  async function fetchDirectoriesTree(payload: FetchTreePayload) {
    directoriesTreeLoading.value = true
    try {
      const response = await axios.post<DirectoryTreeResult>("/vue/get-directories-tree/", {
        project_id: projectId,
        language: currentLanguage.value?.code,
        q: payload.q,
        state: payload.state,
      })
      const { directories_tree: tree } = response.data
      if (tree) directoriesTree.value = tree
    } catch (error) {
      console.error(error)
    } finally {
      directoriesTreeLoading.value = false
    }
  }

  async function deleteString(id: number) {
    const trstring = strings.value.find((el) => el.id === id)
    if (!trstring) return

    trstring.deleted = true

    try {
      await axios.post("/vue/delete-string/", { trstring_id: id })
    } catch (error) {
      console.error(error)
      trstring.deleted = false
    }
  }

  async function saveTranslation(payload: TranslationData) {
    try {
      const response = await axios.post<TrString>("/vue/save-translation/", {
        language: currentLanguage.value?.code,
        ...payload,
      })

      const index = strings.value.findIndex((el) => el.id === response.data.id)
      if (index !== -1) {
        strings.value[index] = response.data
      }
    } catch (e) {
      const error = e as AxiosError
      throw new Error(JSON.stringify(error.response?.data) || "Error saving translation")
    }
  }

  async function addString(payload: TranslationData) {
    try {
      const response = await axios.post<TrString>("/vue/add-string/", {
        project_id: projectId,
        ...payload,
      })
      strings.value.unshift(response.data)
      return response.data
    } catch (e) {
      const error = e as AxiosError
      throw new Error(JSON.stringify(error.response?.data) || "Error adding string")
    }
  }

  async function loadMore(payload: FetchStringsPayload) {
    try {
      const response = await axios.post("/vue/get-strings/", {
        project_id: projectId,
        language: currentLanguage.value?.code,
        dir: payload.dir,
        q: payload.q,
        state: payload.state,
        sort: payload.sort,
        previous_ids: allStringIds.value,
      })

      strings.value = [...strings.value, ...response.data.strings]
      canLoadMore.value = response.data.can_load_more
    } catch (error) {
      console.error(error)
    }
  }

  return {
    addString,
    allStringIds,
    canLoadMore,
    currentLanguage,
    deleteString,
    directoriesTree,
    directoriesTreeLoading,
    fetchDirectoriesTree,
    fetchStrings,
    indexOfString,
    loadMore,
    saveTranslation,
    setLanguage,
    strings,
    updateStringState,
  }
})
