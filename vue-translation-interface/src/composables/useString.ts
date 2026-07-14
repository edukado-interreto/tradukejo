import { useRoute } from "vue-router"
import { useStore } from "@/store"
import { useTranslation } from "./useTranslation"

const translation = useTranslation()

export function useString() {
  const route = useRoute()
  const store = useStore()

  const queryStringDir = computed(() => (route.query.dir as string) || "")

  const queryStringSort = computed(() => (route.query.sort as string) || "")

  const queryStringQ = computed(() => (route.query.q as string) || "")

  const chosenStringId = computed(() => {
    if (route.hash) {
      const id = Number.parseInt(route.hash.substring(1), 10)
      return Number.isNaN(id) ? null : id
    }
    return null
  })

  return {
    queryStringDir,
    queryStringSort,
    queryStringQ,
    chosenStringId,
  }
}
