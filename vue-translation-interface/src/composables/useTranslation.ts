import { useRoute } from "vue-router"
import { vueTranslationInterface } from "@/composables/useGlobals.ts"
import { useStore } from "@/store"

export function useTranslation() {
  const route = useRoute()
  const store = useStore()

  const projectLanguage: string = vueTranslationInterface.projectLanguage

  const editMode = computed(() => projectLanguage === store.currentLanguage?.code)

  const queryStringState = computed(() => {
    if (store.currentLanguage !== null && editMode.value) {
      return ""
    }
    return (route.query.state as string) || ""
  })

  const queryStringDir = computed(() => (route.query.dir as string) || "")

  const queryStringSort = computed(() => (route.query.sort as string) || "")

  const queryStringQ = computed(() => (route.query.q as string) || "")

  const chosenStringId = computed((): number | null => {
    if (route.hash) {
      const id = Number.parseInt(route.hash.substring(1), 10)
      return Number.isNaN(id) ? null : id
    }
    return null
  })

  const translateLink = (parameters: Record<string, any>) => {
    const obj = {
      name: "translateLanguage",
      params: {
        lang: parameters.lang || store.currentLanguage?.code,
      },
      query: {} as Record<string, any>,
    }

    const possibleParameters = ["dir", "state", "sort", "q"]

    possibleParameters.forEach((p) => {
      if (p in parameters) {
        if (parameters[p]) {
          obj.query[p] = parameters[p]
        }
      } else if (route.query[p]) {
        obj.query[p] = route.query[p]
      }
    })

    if (projectLanguage === obj.params.lang) {
      delete obj.query.state
    }

    return obj
  }

  const fetchDirectoriesTree = async () => {
    await store.fetchDirectoriesTree({
      q: queryStringQ.value,
      state: queryStringState.value,
    })
  }

  return {
    editMode,
    queryStringState,
    queryStringDir,
    queryStringSort,
    queryStringQ,
    chosenStringId,
    translateLink,
    fetchDirectoriesTree,
  }
}
