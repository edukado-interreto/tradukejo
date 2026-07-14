<script setup lang="ts">
import { useTranslation } from "@/composables/useTranslation"
import { useGlobals } from "@/composables/useGlobals"
import { useStore } from "@/store"

const store = useStore()

const { availableLanguages } = useGlobals().vueTranslationInterface
const { queryStringDir, translateLink } = useTranslation()

const path = computed<string[]>(() => queryStringDir.value.split("/"))
const pathWithLinks = computed(() => {
  return path.value.map((item, index) => ({
    name: item,
    path: path.value.slice(0, index + 1).join("/"),
  }))
})
</script>

<template>
  <nav aria-label="breadcrumb" class="my-4">
    <ol class="breadcrumb translation-path p-1">
      <li class="breadcrumb-item">
        <span class="dropdown">
          <a
            class="dropdown-toggle"
            href="#"
            type="button"
            id="dropdownLanguageVersionButton"
            data-toggle="dropdown"
            aria-haspopup="true"
            aria-expanded="false"
            >{{ store.currentLanguage?.name }}</a
          >
          <div class="dropdown-menu" aria-labelledby="dropdownLanguageVersionButton">
            <RouterLink
              v-for="language in availableLanguages"
              :key="language.code"
              :to="translateLink({ lang: language.code })"
              class="dropdown-item"
              >{{ language.name }}</RouterLink
            >
          </div>
        </span>
      </li>

      <li class="breadcrumb-item">
        <RouterLink v-if="path.length > 0 && path[0] != ''" :to="translateLink({ dir: '' })"
          ><i class="fas fa-home"></i>
        </RouterLink>
        <span v-else><i class="fas fa-home"></i></span>
      </li>
      <li
        v-for="(directory, index) in pathWithLinks"
        :key="index"
        :aria-current="index === pathWithLinks.length - 1 ? 'page' : undefined"
        class="breadcrumb-item"
      >
        <RouterLink
          v-if="index < pathWithLinks.length - 1"
          :to="translateLink({ dir: directory.path })"
        >
          {{ directory.name }}
        </RouterLink>
        <template v-else>{{ directory.name }}</template>
      </li>
    </ol>
  </nav>
</template>

<style lang="scss" scoped>
.breadcrumb.translation-path {
  background: none;
  font-size: 1rem;
}
</style>
