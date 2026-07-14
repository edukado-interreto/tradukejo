<script setup lang="ts">
import { useRouter } from "vue-router"
import { useI18n } from "vue-i18n"
import { useTranslation } from "@/composables/useTranslation"
import { useGlobals } from "@/composables/useGlobals"

const {
  vueTranslationInterface: { globals },
} = useGlobals()

const router = useRouter()
const { t } = useI18n()
const { editMode, translateLink, queryStringQ, queryStringState, queryStringSort } =
  useTranslation()

const searchString = ref(queryStringQ.value)

const stateFilters = computed(() => ({
  [globals.STATE_FILTER_ALL]: t("filters.all"),
  [globals.STATE_FILTER_UNTRANSLATED]: t("filters.untranslated"),
  [globals.STATE_FILTER_OUTDATED]: t("filters.outdated"),
  [globals.STATE_FILTER_OUTDATED_UNTRANSLATED]: t("filters.untranslated_outdated"),
}))

const sortFilters = computed(() => ({
  [globals.SORT_STRINGS_BY_NAME]: t("filters.order_name"),
  [globals.SORT_STRINGS_BY_OLDEST]: t("filters.order_old"),
  [globals.SORT_STRINGS_BY_NEWEST]: t("filters.order_new"),
}))

const currentStateFilter = computed(() => {
  const filters = stateFilters.value
  return filters[queryStringState.value] || Object.values(filters)[0]
})

const currentSortFilter = computed(() => {
  const filters = sortFilters.value
  return filters[queryStringSort.value] || Object.values(filters)[0]
})

const search = () => {
  router.push(translateLink({ q: searchString.value }))
}

const clearSearch = () => {
  searchString.value = ""
  search()
}
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <ul class="navbar-nav mr-auto">
      <!-- State Dropdown -->
      <li v-if="!editMode" class="nav-item dropdown">
        <a
          class="nav-link dropdown-toggle"
          href="#"
          id="stringStateDropdown"
          role="button"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          {{ currentStateFilter }}
        </a>
        <div class="dropdown-menu" aria-labelledby="stringStateDropdown">
          <RouterLink
            v-for="(name, key) in stateFilters"
            :key="key"
            class="dropdown-item"
            :to="translateLink({ state: key })"
          >
            {{ name }}
          </RouterLink>
        </div>
      </li>

      <!-- Sort Dropdown -->
      <li class="nav-item dropdown">
        <a
          class="nav-link dropdown-toggle"
          href="#"
          id="sortDropdown"
          role="button"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          {{ currentSortFilter }}
        </a>
        <div class="dropdown-menu" aria-labelledby="sortDropdown">
          <RouterLink
            v-for="(name, key) in sortFilters"
            :key="key"
            class="dropdown-item"
            :to="translateLink({ sort: key })"
          >
            {{ name }}
          </RouterLink>
        </div>
      </li>
    </ul>

    <!-- Search Form -->
    <form class="form-inline my-2 my-lg-0" @submit.prevent="search">
      <div class="search-container d-flex align-items-center">
        <input
          class="form-control mr-sm-2"
          type="search"
          :placeholder="t('filters.search') + '…'"
          :aria-label="t('filters.search')"
          v-model="searchString"
        />
        <button v-if="searchString" class="clear-search" type="button" @click="clearSearch">
          <i class="fas fa-times-circle" />
        </button>
      </div>
      <button class="btn btn-secondary" type="submit">
        {{ t("filters.search") }}
      </button>
    </form>
  </nav>
</template>

<style lang="scss" scoped>
.search-container {
  position: relative;
}

.clear-search {
  background: none;
  border: none;
  margin: 0;
  padding: 0;
  position: absolute;
  right: 1.25em; /* Adjusted to sit inside the input better */
  color: #a8a8a8;
  cursor: pointer;

  &:hover {
    color: #797979;
  }
}
</style>
