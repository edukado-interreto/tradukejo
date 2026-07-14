<script setup lang="ts">
import { useRoute, useRouter, onBeforeRouteLeave, onBeforeRouteUpdate } from "vue-router"
import { useI18n } from "vue-i18n"
import { useStore } from "@/store"
import { useTranslation } from "@/composables/useTranslation"

const store = useStore()
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const {
  queryStringDir,
  queryStringQ,
  queryStringState,
  queryStringSort,
  chosenStringId,
  fetchDirectoriesTree,
} = useTranslation()

const isLoading = ref(false)
const directoriesTreeLoadedOnce = ref(false)

const dirLoading = computed(() => store.directoriesTreeLoading)
const paramLang = computed(() => route.params.lang as string)

const directories = computed(() => {
  let currentDir = store.directoriesTree[""]
  if (!currentDir) return {}

  if (queryStringDir.value !== "") {
    const segments = queryStringDir.value.split("/")
    let notFound = false
    segments.forEach((d) => {
      if (currentDir?.children && d in currentDir.children) {
        currentDir = currentDir.children[d]
      } else {
        notFound = true
      }
    })
    if (notFound) return {}
  }
  return currentDir.children || {}
})

const noDirectories = computed(() => {
  return (
    !store.directoriesTreeLoading &&
    Object.keys(store.directoriesTree[""]?.children || {}).length === 0
  )
})

const fetchStrings = async () => {
  isLoading.value = true
  await store.fetchStrings({
    dir: queryStringDir.value,
    q: queryStringQ.value,
    state: queryStringState.value,
    sort: queryStringSort.value,
    chosen_string: chosenStringId.value,
  })
  isLoading.value = false
}

const isAllowedToLeave = () => {
  const saveButtons = document.querySelectorAll("#app .can-submit")
  if (saveButtons.length > 0) {
    return window.confirm(
      "Vi havas nekonservitajn ŝanĝojn, ĉu vi certe volas eliri el ĉi tiu paĝo?",
    )
  }
  return true
}

const handlerClose = (e: BeforeUnloadEvent) => {
  if (!isAllowedToLeave()) e.preventDefault()
}

watch(paramLang, (code) => {
  store.setLanguage(code)
  fetchStrings()
  fetchDirectoriesTree()
})

watch([queryStringState, queryStringQ], () => {
  fetchStrings()
  fetchDirectoriesTree()
})

watch([queryStringSort, queryStringDir], () => {
  fetchStrings()
})

watch(dirLoading, (newVal) => {
  if (!newVal) {
    directoriesTreeLoadedOnce.value = true
  }
})

// init
store.setLanguage(paramLang.value)
fetchStrings()
fetchDirectoriesTree()

onMounted(() => {
  if (!store.currentLanguage) {
    router.push({ name: "languageChoice" })
  }
  window.addEventListener("beforeunload", handlerClose)
})

onUnmounted(() => {
  window.removeEventListener("beforeunload", handlerClose)
})

onBeforeRouteUpdate(isAllowedToLeave)
onBeforeRouteLeave(isAllowedToLeave)
</script>

<template>
  <filter-bar />
  <navigation-bar />

  <div class="row">
    <div v-if="!noDirectories" class="col-12 col-lg-3 col-xl-2">
      <div class="card mb-3">
        <div class="card-body">
          <loading-spinner v-if="store.directoriesTreeLoading" small />
          <directories-tree v-else :tree="store.directoriesTree" />
        </div>
      </div>
    </div>
    <div class="col">
      <directories-list v-if="directoriesTreeLoadedOnce" :directories="directories" />
      <loading-spinner v-if="isLoading" />
      <translation-zone v-else :strings="store.strings" />

      <div
        v-if="
          store.strings.length === 0 &&
          !isLoading &&
          !store.directoriesTreeLoading &&
          Object.keys(directories).length === 0
        "
        class="alert alert-info"
      >
        {{ t("translate.no_result") }}
      </div>
    </div>
  </div>
</template>
